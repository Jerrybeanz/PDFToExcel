import sys
import xlwings as xw
from xlwings import constants as xl_constants
import sqlite3
import pandas as pd
from datetime import date
from master_list_tables import *


def validate_date(sheet, table_range, column):
    validation = sheet.range(f"{column}2:{column}{table_range.last_cell.row}").api.Validation
    validation.Delete()
    min_date = date(1900, 1, 1).toordinal() - 693594
    max_date = date.today().toordinal() - 693594

    validation.Add(
        Type=xl_constants.DVType.xlValidateDate,
        AlertStyle=xl_constants.DVAlertStyle.xlValidAlertStop,
        Operator=xl_constants.FormatConditionOperator.xlBetween,
        Formula1=min_date,
        Formula2=max_date
    )

    validation.InputTitle = "Date Entry"
    validation.InputMessage = "Enter a valid date between 1900-01-01 and today"


def validate_number(sheet, table_range, column):
    validation = sheet.range(f"{column}2:{column}{table_range.last_cell.row}").api.Validation
    validation.Delete()

    validation.Add(
        Type=xl_constants.DVType.xlValidateWholeNumber,
        AlertStyle=xl_constants.DVAlertStyle.xlValidAlertStop,
        Operator=xl_constants.FormatConditionOperator.xlGreater,
        Formula1=0,
        Formula2=None
    )

    validation.InputTitle = "Number Entry"
    validation.InputMessage = "Enter a valid number greater than 0"


def validate_uen(sheet, table_range, column):
    validation = sheet.range(f"{column}2:{column}{table_range.last_cell.row}").api.Validation
    validation.Delete()
    formula = f"=AND(LEN({column}2)=10, ISNUMBER(VALUE(LEFT({column}2,9))), NOT(ISNUMBER(VALUE(RIGHT({column}2,1)))))"

    validation.Add(
        Type=xl_constants.DVType.xlValidateCustom,
        AlertStyle=xl_constants.DVAlertStyle.xlValidAlertWarning,
        Operator=xl_constants.FormatConditionOperator.xlEqual,
        Formula1=formula,
        Formula2=None
    )

    validation.ErrorTitle = "Abnormal UEN format"
    validation.ErrorMessage = "UEN format is usually 9 digits followed by a letter"


def protect_table(sheet, table, table_range):
    sheet.api.Cells.Locked = False
    header_range = sheet.range("A1").expand("right")

    for cell in header_range:
        if cell.value in master_list_tables[table.name].headers:
            cell.api.Locked = True

    data_range = sheet.range(f"A2:{table_range.last_cell.address}")
    data_range.api.Locked = False

    sheet.api.Protect(
        DrawingObjects=True,  # Protect shapes/charts
        Contents=True,  # Protect cells
        Scenarios=True,  # Protect scenarios
        UserInterfaceOnly=True,  # Allow VBA macros
        AllowFormattingCells=True,  # Users can format cells
        AllowFormattingColumns=True,  # Users can format columns
        AllowFormattingRows=True,  # Users can format rows
        AllowInsertingColumns=True,  # Allow column insertion
        AllowInsertingRows=False,  # Prevent row insertion
        AllowDeletingColumns=False,  # Prevent column deletion
        AllowDeletingRows=False,  # Prevent row deletion
        AllowSorting=True,  # Allow sorting
        AllowFiltering=True,  # Allow filtering
        AllowUsingPivotTables=True  # Allow pivot tables
    )


def get_data_from_db(database_path=None):
    if database_path is None:
        # Running as exe file from Excel VBA
        if getattr(sys, 'frozen', False):
            database_path = sys.argv[1]
        else:
            database_path = "MasterList.db"

    if getattr(sys, 'frozen', False):
        # Running as EXE - use active instance
        app = xw.apps.active
        wb = app.books.active
    else:
        # Running as script - use caller for debugging
        xw.Book("template.xlsm").set_mock_caller()
        wb = xw.Book.caller()


    with sqlite3.connect(database_path) as conn:
        for table in (companies_table, people_table, positions_table):
            sql_query = f'SELECT * FROM "{table.name}"'
            df = pd.read_sql(sql_query, conn)
            found_table = False

            for sheet in wb.sheets:
                # Overwrite existing table
                if table.name in sheet.tables:
                    # Unprotect first
                    sheet.api.Unprotect()

                    # Update table
                    excel_table = sheet.tables[table.name]
                    excel_table.update(df, index=False)
                    table_range = excel_table.range
                    table_range.autofit()

                    # Reprotect
                    protect_table(sheet, table, table_range)

                    found_table = True
                    break

            # Create new table
            if not found_table:
                if table.name not in wb.sheets:
                    sheet = wb.sheets.add(table.name)
                else:
                    sheet = wb.sheets[table.name]

                sheet.clear()
                sheet.range('A1').options(index=False).value = df

                # Convert to Excel table
                last_cell = sheet.range('A1').expand('table').last_cell
                table_range = sheet.range(f'A1:{last_cell.address}')
                table_range.autofit()

                # Create the table
                new_table = sheet.api.ListObjects.Add(1,  # xlSrcRange
                                                      table_range.api,
                                                      None,  # Source
                                                      1)  # xlYes (headers)
                new_table.Name = table.name

                # Enforce data validation
                if table is companies_table:
                    for column in 'ADFIKLMN':
                        validate_date(sheet, table_range, column)

                    for column in 'QRUV':
                        validate_number(sheet, table_range, column)

                    validate_uen(sheet, table_range, 'E')

                # Protect table
                protect_table(sheet, table, table_range)


if __name__ == '__main__':
    get_data_from_db()