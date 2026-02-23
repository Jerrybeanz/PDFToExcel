import re
import pandas as pd


class GenericParser:
    def __init__(self):
        self.tables = []
        self.single_table = False

    def parse(self, pdf):
        for page in pdf.pages:
            parsed_tables = page.extract_tables()
            for table in parsed_tables:
                start_row_idx = len(table)

                # Find valid header
                for index, row in enumerate(table):
                    valid_header = True

                    for col in row:
                        if col is None or col == '' or col == ' ' * len(col):
                            valid_header = False

                    if valid_header:
                        start_row_idx = index
                        break

                if start_row_idx != len(table):
                    table = table[start_row_idx:]

                    # Table header matches with previous table header, join them together
                    if self.tables and table[0] == self.tables[-1][0]:
                        self.tables[-1].extend(table[1:])
                    else:
                        self.tables.append(table)


class OCBCParser:
    def __init__(self):
        self.file_header = "OCBC Bank"
        self.table_name = "OCBC"
        self.header_row = ["Transaction Date", "Value Date", "Description", "Cheque", "Withdrawal", "Deposit", "Balance"]
        self.table = [self.header_row]

    def parse(self, pdf):
        current_transaction = None
        prev_balance = 0
        year = 2026
        found_year = False
        period_pattern = re.compile(r'\d{1}\s*[A-Z]{3}\s*\d{4} TO \d{2}\s*[A-Z]{3}\s*\d{4}')
        row_start_pattern = re.compile(r'\d{2}\s*[A-Z]{3}\s*\d{2}\s*[A-Z]{3}')

        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')

            for line in lines:
                if not found_year:
                    # Detect period of transaction
                    period_match = period_pattern.search(line)
                    if period_match is not None:
                        idx = period_match.start()
                        year = int(line[idx+6:idx+10])
                        found_year = True

                if line.startswith("BALANCE"):
                    if current_transaction is not None:
                        self.table.append(current_transaction)

                    data = line.split(' ')
                    balance = float(data[-1].replace(',', ''))
                    current_transaction = None
                    prev_balance = balance

                elif row_start_pattern.match(line):
                    if current_transaction is not None:
                        self.table.append(current_transaction)

                    data = line.split(' ')

                    transaction_date = pd.to_datetime(data[0] + ' ' + data[1] + f" {year}", format = '%d %b %Y')
                    value_date = pd.to_datetime(data[2] + ' ' + data[3] + f" {year}", format = '%d %b %Y')

                    if data[4] == "CHEQUE" and data[5].isdigit() and len(data[5]) == 6:
                        description = data[4]
                        cheque = data[5]
                    else:
                        description = " ".join(data[4:-2])
                        cheque = None

                    amount = float(data[-2].replace(',', ''))
                    balance = float(data[-1].replace(',', ''))

                    current_transaction = [
                        transaction_date,
                        value_date,
                        description,
                        cheque,
                        amount if balance < prev_balance else 0,
                        amount if balance > prev_balance else 0,
                        balance
                    ]

                    prev_balance = balance

                elif line == "Please turn over …":
                    if current_transaction is not None:
                        self.table.append(current_transaction)
                    current_transaction = None

                elif current_transaction:
                    current_transaction[2] += ' ' + line


class CPFParser:
    def __init__(self):
        self.file_header = "View Employer Submission"
        self.table_name = "CPF"
        self.header_row = ["Month", "NRIC", "Employee Name", "Total CPF", "SDL", "Employer CPF", "Employee CPF", "Ordinary Wages", "Additional Wages", "Agency", "Agency Fund"]
        self.table = [self.header_row]

    def parse(self, pdf):
        month = None
        found_month = False
        row_start_pattern = re.compile(r'\d+.\s*[A-Z]{1}\d{7}[A-Z]{1}')

        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')

            for line in lines:
                if not found_month and line.startswith("Month Paid For"):
                    data = line.split(' ')
                    month = ' '.join(data[4:6])
                    found_month = True

                elif row_start_pattern.match(line):
                    data = line.split(' ')
                    _id = data[1]
                    name = ' '.join(data[2:-8])
                    total_cpf = float(data[-8].replace(',', ''))
                    sdl = float(data[-7].replace(',', ''))
                    employer_cpf = float(data[-6].replace(',', ''))
                    employee_cpf = float(data[-5].replace(',', ''))
                    ordinary_wages = float(data[-4].replace(',', ''))
                    additional_wages = float(data[-3].replace(',', ''))
                    agency = data[-2]
                    agency_fund = float(data[-1].replace(',', ''))

                    row = [
                        month,
                        _id,
                        name,
                        total_cpf,
                        sdl,
                        employer_cpf,
                        employee_cpf,
                        ordinary_wages,
                        additional_wages,
                        agency,
                        agency_fund
                    ]
                    self.table.append(row)