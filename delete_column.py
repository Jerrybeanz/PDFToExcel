import sys
import xlwings as xw
import sqlite3
from master_list_tables import *


def delete_column(database_path=None):
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

    table_name = sys.argv[2]
    column_name = sys.argv[3]

    print(table_name, column_name)

    if column_name in master_list_tables[table_name].headers:
        print("Error deleting column, column is default")
        return

    print("Column deleted successfully!")

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()


if __name__ == '__main__':
    delete_column()