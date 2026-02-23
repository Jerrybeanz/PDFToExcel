from tkinter import filedialog as fd
import pandas as pd
import sqlite3
import os
from parse_pdf import parse_pdf


def export_pdf_to_file():
    tables = parse_pdf()
    output_file = fd.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("Database files", "*.db")], initialfile="output")

    if not output_file:
        print("No output file selected")
        return

    file_type = output_file.split(".")[-1]

    if file_type == "xlsx":
        with pd.ExcelWriter(output_file, datetime_format='dd-mmm-yyyy') as writer:
            for table_name, table in tables.items():
                df = pd.DataFrame(table)
                df.to_excel(writer, sheet_name=table_name, index=False, header=False)

        os.startfile(output_file)

    elif file_type == "db":
        with sqlite3.connect(output_file) as connection:
            for table_name, table in tables.items():
                df = pd.DataFrame(table[1:], columns=table[0])
                df.to_sql(table_name, connection, if_exists="replace", index=False)


if __name__ == '__main__':
    export_pdf_to_file()