import sys
import tkinter as tk
from tkinter import filedialog as fd
import pdfplumber
import pandas as pd
from master_list_tables import *
from master_list_parsers import BusinessProfileParser
from sync_to_db import sync_to_db
from get_data_from_db import get_data_from_db
from upsert_from_table import upsert_from_table


def upload_bizfile(excel_path=None, database_path=None):
    if excel_path is None and database_path is None:
        if getattr(sys, 'frozen', False):
            excel_path = sys.argv[1]
            database_path = sys.argv[2]
        else:
            excel_path = "template.xlsm"
            database_path = "MasterList.db"

    # Sync to db first
    sync_to_db(excel_path=excel_path, database_path=database_path)

    root = tk.Tk()
    root.withdraw()
    file_paths = fd.askopenfilenames(parent=root, title="Select pdf files", filetypes=[("PDF files", "*.pdf")])
    root.destroy()

    if not file_paths:
        print("No files selected")
        return

    business_profile_parser = BusinessProfileParser()

    # Process files
    for file_path in file_paths:
        with pdfplumber.open(file_path) as pdf:
            # Detect file type from first page
            text = pdf.pages[0].extract_text()
            if text.startswith(business_profile_parser.file_header):
                business_profile_parser.parse(pdf)

    # Update in database
    upsert_from_table(companies_table, pd.DataFrame(companies_table.table), database_path)
    upsert_from_table(people_table, pd.DataFrame(people_table.table), database_path)
    upsert_from_table(positions_table, pd.DataFrame(positions_table.table), database_path)

    # Pull changes in database to Excel
    get_data_from_db(database_path=database_path)


if __name__ == "__main__":
    upload_bizfile()