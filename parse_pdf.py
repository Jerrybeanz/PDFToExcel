import tkinter as tk
from tkinter import filedialog as fd
import pdfplumber
from parsers import ParserManager


def parse_pdf():
    """
    Returns a list of Table objects after parsing pdf files.
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_paths = fd.askopenfilenames(parent=root, title="Select pdf files", filetypes=[("PDF files", "*.pdf")])
    root.destroy()

    if not file_paths:
        print("No files selected")
        return []

    for file_path in file_paths:
        with pdfplumber.open(file_path) as pdf:
            current_parser = ParserManager.find_parser(pdf)

            if current_parser is None:
                print(f"No parser found for {file_path}!")
                continue

            current_parser.parse(pdf)

    tables = []

    for parser in ParserManager.all_parsers():
        for table in parser.tables:
            # Table is not empty
            if table.rows:
                tables.append(table)

    return tables


if __name__ == '__main__':
    parse_pdf()