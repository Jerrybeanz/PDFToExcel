import tkinter as tk
from tkinter import filedialog as fd
import pdfplumber
import re
import pandas as pd
import os


def parse_ocbc_statements(file_paths):
    """
    Takes a list of paths to OCBC bank statement PDF files and parses them into a dataframe
    """
    transactions = []
    date_pattern = r'^(\d{2}\s+[A-Z]{3})'

    for file_path in file_paths:
        with pdfplumber.open(file_path) as pdf:
            current_transaction = None
            prev_balance = 0

            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split('\n')

                for line in lines:
                    if line.startswith("BALANCE B/F") or line.startswith("BALANCE C/F"):
                        if current_transaction is not None:
                            transactions.append(current_transaction)

                        data = line.split(' ')
                        description = ' '.join(data[:2])
                        balance = float(data[-1].replace(',', ''))
                        transaction = {
                            "Transaction Date": None,
                            "Value Date": None,
                            "Description": description,
                            "Cheque": None,
                            "Withdrawal": None,
                            "Deposit": None,
                            "Balance": balance
                        }
                        transactions.append(transaction)
                        current_transaction = None
                        prev_balance = balance

                    elif re.match(date_pattern, line):
                        if current_transaction is not None:
                            transactions.append(current_transaction)

                        data = line.split(' ')
                        transaction_date = data[0] + ' ' + data[1]
                        value_date = data[2] + ' ' + data[3]

                        if data[4] == "CHEQUE" and data[5].isdigit() and len(data[5]) == 6:
                            description = data[4]
                            cheque = data[5]
                        else:
                            description = " ".join(data[4:-2])
                            cheque = None

                        amount = float(data[-2].replace(',', ''))
                        balance = float(data[-1].replace(',', ''))

                        current_transaction = {
                            "Transaction Date": transaction_date,
                            "Value Date": value_date,
                            "Description": description,
                            "Cheque": cheque,
                            "Withdrawal": amount if balance < prev_balance else 0,
                            "Deposit": amount if balance > prev_balance else 0,
                            "Balance": balance
                        }

                        prev_balance = balance

                    elif line == "Please turn over …":
                        if current_transaction is not None:
                            transactions.append(current_transaction)
                        current_transaction = None

                    elif current_transaction:
                        current_transaction["Description"] += ' ' + line

    df = pd.DataFrame(transactions)
    return df


def pdf_to_excel():
    root = tk.Tk()
    root.withdraw()
    file_paths = fd.askopenfilenames(parent=root, title="Select pdf files", filetypes=[("PDF files", "*.pdf")])
    root.destroy()

    if not file_paths:
        print("No files selected")
        return

    df = parse_ocbc_statements(file_paths)
    output_file = fd.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], initialfile="transactions.xlsx")

    if not output_file:
        print("No output file selected")
        return

    with pd.ExcelWriter(output_file) as writer:
        df.to_excel(writer, sheet_name="Sheet", index=False, header=True)

    os.startfile(output_file)


pdf_to_excel()