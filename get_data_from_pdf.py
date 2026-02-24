import xlwings as xw
import pandas as pd
import sys
from parse_pdf import parse_pdf


def get_data_from_pdf():
    """
    To be used for an Excel VBA macro
    """
    # Check if we're running as a frozen EXE
    if getattr(sys, 'frozen', False):
        # Running as EXE - use active instance
        app = xw.apps.active
        wb = app.books.active
    else:
        # Running as script - use caller for debugging
        xw.Book("template.xlsm").set_mock_caller()
        wb = xw.Book.caller()

    tables = parse_pdf()

    for table_name, table in tables.items():
        df = pd.DataFrame(table[1:], columns=table[0])
        found_table = False

        for sheet in wb.sheets:
            # Append to existing table
            if table_name in sheet.tables:
                table_range = sheet.tables[table_name].range

                last_row = table_range.last_cell.row
                start_cell = sheet.range(f"A{last_row + 1}")
                start_cell.options(index=False, header=False).value = df.values.tolist()

                # Autofit columns
                sheet.range('A1').expand('table').columns.autofit()

                found_table = True
                break

        # Create new sheet and table
        if not found_table:
            if table_name not in wb.sheets:
                sheet = wb.sheets.add(table_name)
            else:
                sheet = wb.sheets[table_name]

            sheet.clear()
            sheet.range('A1').options(index=False).value = df

            # Convert to Excel table
            last_cell = sheet.range('A1').expand('table').last_cell
            table_range = sheet.range(f'A1:{last_cell.address}')

            # Create the table
            new_table = sheet.api.ListObjects.Add(
                                      1,  # xlSrcRange
                                      table_range.api,
                                      None,  # Source
                                      1)  # xlYes (headers)
            new_table.Name = table_name

            # Autofit columns
            table_range.autofit()


if __name__ == "__main__":
    get_data_from_pdf()