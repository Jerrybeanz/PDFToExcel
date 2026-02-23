import sys
import xlwings as xw
import sqlite3
import pandas as pd
from master_list_tables import *


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

            try:
                sheet = wb.sheets.add(table.name)
            except:
                sheet = wb.sheets[table.name]

            sheet.clear()
            sheet.range('A1').options(index=False).value = df

            # Convert to Excel table
            last_cell = sheet.range('A1').expand('table').last_cell
            table_range = f'A1:{last_cell.address}'

            # Create the table
            new_table = sheet.api.ListObjects.Add(1,  # xlSrcRange
                                                  sheet.range(table_range).api,
                                                  None,  # Source
                                                  1)  # xlYes (headers)
            new_table.Name = table.name


if __name__ == '__main__':
    get_data_from_db()