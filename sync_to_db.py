import sqlite3
import sys
import pandas as pd
from master_list_tables import *
from upsert_from_table import upsert_from_table


def sync_to_db(excel_path=None, database_path=None):
    if excel_path is None and database_path is None:
        # Running as exe file from Excel VBA
        if getattr(sys, 'frozen', False):
            excel_path = sys.argv[1]
            database_path = sys.argv[2]
        else:
            excel_path = "template.xlsm"
            database_path = "MasterList.db"

    # Read Excel
    excel_file = pd.read_excel(excel_path, sheet_name=None)

    # Write to SQLite
    for table_name in ("Positions", "Companies", "People"):
        if table_name in excel_file:
            with sqlite3.connect(database_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute(f'DELETE FROM "{table_name}";')
                conn.commit()

    for table_name in ("Companies", "People", "Positions"):
        if table_name in excel_file:
            table = master_list_tables[table_name]
            df = excel_file[table_name]
            upsert_from_table(table, df, database_path)


if __name__ == "__main__":
    sync_to_db()