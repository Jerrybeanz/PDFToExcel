import tkinter as tk
from tkinter import filedialog as fd
import pdfplumber
import re
from parsers import OCBCParser, CPFParser, GenericParser


def parse_pdf():
    generic_parser = GenericParser()
    ocbc_parser = OCBCParser()
    cpf_parser = CPFParser()
    parsers = [ocbc_parser, cpf_parser]
    root = tk.Tk()
    root.withdraw()
    file_paths = fd.askopenfilenames(parent=root, title="Select pdf files", filetypes=[("PDF files", "*.pdf")])
    root.destroy()

    if not file_paths:
        print("No files selected")
        return {}

    for file_path in file_paths:
        with pdfplumber.open(file_path) as pdf:
            # Detect file type
            current_parser = None

            for page in pdf.pages:
                text = page.extract_text()
                if re.search(r'OCBC', text):
                    current_parser = ocbc_parser
                    break

                elif re.search(r'CPF', text):
                    current_parser = cpf_parser
                    break

            # Use generic parser if no specialised parsers found
            if current_parser is None:
                current_parser = generic_parser

            current_parser.parse(pdf)

    tables = {}

    for parser in parsers:
        if len(parser.table) > 1:
            tables[parser.table_name] = parser.table

    for table_number, table in enumerate(generic_parser.tables, start=1):
        tables[f"Table {table_number}"] = table

    return tables


if __name__ == '__main__':
    tables = parse_pdf()
    for table_name, table in tables.items():
        print(table_name)
        print(table)