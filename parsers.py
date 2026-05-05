import re
import pandas as pd


class ParserManager(type):
    _registry = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name != "Parser": # Ignore base Parser class
            ParserManager._registry[name] = cls

    @classmethod
    def get_parser(mcs, name):
        return mcs._registry[name]

    @classmethod
    def all_parsers(mcs):
        return iter(mcs._registry.values())

    @classmethod
    def find_parser(mcs, pdf):
        """
        Finds correct parser for given pdf, based on file header
        :param pdf: pdf object from pdfplumber
        :return: parser object
        """
        for page in pdf.pages:
            text = page.extract_text()
            for parser in ParserManager.all_parsers():
                if isinstance(parser.file_header, str):
                    if parser.file_header in text:
                        return parser
                else:
                    for header in parser.file_header:
                        if header in text:
                            return parser

        return None


class Parser(metaclass=ParserManager):
    pass


class Table:
    def __init__(self, name, headers):
        self.name = name
        self.headers = headers
        self.rows = []

# For comma-separated numbers with decimals
def to_float(x):
    return float(x.replace(',', ''))


class OCBCParser(Parser):
    file_header = "OCBC Bank"
    ocbc_table = Table("OCBC", ["Transaction Date", "Value Date", "Description", "Cheque", "Withdrawal", "Deposit", "Balance"])
    tables = [ocbc_table]
    period_pattern = re.compile(r'\d{1}\s*[A-Z]{3}\s*\d{4} TO \d{2}\s*[A-Z]{3}\s*\d{4}')  # E.g. 1 DEC 2024 TO 31 DEC 2024
    row_start_pattern = re.compile(r'\d{2}\s*[A-Z]{3}\s*\d{2}\s*[A-Z]{3}')  # E.g. 01 DEC 02 DEC
    number_pattern = re.compile(r'(\d{1,3},)?(\d{3},)*\d{1,3}\.\d{2}')  # E.g. 5,500,500.00

    @classmethod
    def parse(cls, pdf):
        year = None
        current_transaction = None
        prev_balance = 0

        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')

            for line in lines:
                if year is None:
                    # Detect period of transaction
                    period_match = cls.period_pattern.search(line)
                    if period_match is not None:
                        idx = period_match.start()
                        year = int(line[idx+6:idx+10])

                # For opening/closing balance
                elif line.startswith("BALANCE"):
                    if current_transaction is not None:
                        cls.ocbc_table.rows.append(current_transaction)

                    current_transaction = None
                    data = line.split(' ')
                    prev_balance = float(data[-1].replace(',', ''))

                # Start of transaction
                elif cls.row_start_pattern.match(line):
                    if current_transaction is not None:
                        cls.ocbc_table.rows.append(current_transaction)

                    data = line.split(' ')

                    # Skip invalid data at the back
                    while data and not cls.number_pattern.fullmatch(data[-1]):
                        data.pop()

                    transaction_date = pd.to_datetime(data[0] + ' ' + data[1] + f" {year}", format = '%d %b %Y')
                    value_date = pd.to_datetime(data[2] + ' ' + data[3] + f" {year}", format = '%d %b %Y')

                    if data[4] == "CHEQUE" and data[5].isdigit() and len(data[5]) == 6:
                        description = data[4]
                        cheque = data[5]
                    else:
                        description = " ".join(data[4:-2])
                        cheque = None

                    amount = to_float(data[-2])
                    balance = to_float(data[-1])

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

                # End of page
                elif line == "Please turn over …":
                    if current_transaction is not None:
                        cls.ocbc_table.rows.append(current_transaction)
                    current_transaction = None

                # Continuation of previous transaction, add to description
                elif current_transaction:
                    current_transaction[2] += ' ' + line

        cls.ocbc_table.rows.sort(key=lambda row: row[0])  # Sort by date


class DBSParser(Parser):
    file_header = "DBS Bank"
    dbs_table = Table("DBS", ["Transaction Date", "Value Date", "Transaction Details", "Withdrawal", "Deposit", "Balance"])
    tables = [dbs_table]
    row_start_pattern = re.compile(r'\d{2}-[A-Z][a-z]{2}-\d{2}\s*\d{2}-[A-Z][a-z]{2}-\d{2}')  # E.g. 06-Jan-25 06-Jan-25
    number_pattern = re.compile(r'(\d{1,3},)?(\d{3},)*\d{1,3}\.\d{2}')  # E.g. 5,500,500.00

    @classmethod
    def parse(cls, pdf):
        current_transaction = None
        prev_balance = 0
        start = False # Skip headers

        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')

            for line in lines:
                # Start of statement
                if not start and line.startswith("Balance Brought Forward"):
                    data = line.split(' ')
                    prev_balance = to_float(data[-1])
                    start = True

                # Start of transaction
                elif cls.row_start_pattern.match(line):
                    if current_transaction is not None:
                        cls.dbs_table.rows.append(current_transaction)

                    data = line.split(' ')

                    # Skip invalid data at the back
                    while data and not cls.number_pattern.fullmatch(data[-1]):
                        data.pop()

                    transaction_date = pd.to_datetime(data[0], format="%d-%b-%y")
                    value_date = pd.to_datetime(data[1], format="%d-%b-%y")

                    description = " ".join(data[2:-2])

                    amount = to_float(data[-2])
                    balance = to_float(data[-1])

                    current_transaction = [
                        transaction_date,
                        value_date,
                        description,
                        amount if balance < prev_balance else 0,
                        amount if balance > prev_balance else 0,
                        balance
                    ]

                    prev_balance = balance

                # End of page
                elif line == "3-0810058-RM" or line == "DBS Bank Ltd":
                    if current_transaction is not None:
                        cls.dbs_table.rows.append(current_transaction)
                    current_transaction = None

                # End of statement
                elif line.startswith("Total"):
                    if current_transaction is not None:
                        cls.dbs_table.rows.append(current_transaction)

                    current_transaction = None
                    break

                # Continuation of previous transaction, add to description
                elif current_transaction:
                    current_transaction[2] += ' ' + line

        cls.dbs_table.rows.sort(key=lambda row: row[0]) # Sort by date


class AspireParser(Parser):
    file_header = "Aspire"
    aspire_table = Table("Aspire", ["Date & time", "Counterparty", "Description", "Debit (SGD)", "Credit (SGD)", "Balance (SGD)"])
    tables = [aspire_table]

    @classmethod
    def parse(cls, pdf):
        row_start_pattern = re.compile(r'\d*\s*\d{2}\s*[A-Z][a-z]{2}\s*\d{4}') # E.g. 1 01 Jan 2025 (Row number followed by date)
        date_pattern = re.compile(r'\d{2}\s*[A-Z][a-z]{2}\s*\d{4}') # E.g. 01 Jan 2025
        number_pattern = re.compile(r'(\d{1,3},)?(\d{3},)*\d{1,3}\.\d{2}') # E.g. 5,500,500.00
        start = False # Skip through headers

        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')

            for line in lines:
                if not start:
                    # Start of transactions
                    if line.startswith("# Date & time"):
                        start = True
                    else:
                        continue

                if row_start_pattern.match(line):
                    date_match = date_pattern.search(line)
                    date = line[date_match.start():date_match.end()]
                    first_number_match = number_pattern.search(line)
                    counterparty = line[date_match.end():first_number_match.start()]
                    first_number = line[first_number_match.start():first_number_match.end()]

                    # Means first number is Debit, Credit is empty.
                    if '-' in line[first_number_match.end():]:
                        debit = first_number
                        credit = 0
                    else:
                        debit = 0
                        credit = first_number

                    second_number_match = number_pattern.search(line[first_number_match.end():])
                    second_number = line[second_number_match.start() + first_number_match.end():second_number_match.end() + first_number_match.end()]

                    row = [date, counterparty, "", debit, credit, second_number]
                    cls.aspire_table.rows.append(row)


class CPFEzPayParser(Parser):
    file_header = ("CPF EZPay", "View Employer Submission") # There are actually 2 very similar pdf files for CPF EzPay, one starting with "CPF EzPay" and the other "View Employer Submission"
    summary_table = Table("CPF_Summary", ["Month", "Total CPF Contributions", "CPF Late Payment Interest", "Skills Development Levy (SDL)", "Donation to Community Chest",
                                          "Total MBMF Contributions", "Total SINDA Contributions", "Total CDAC Contributions", "Total ECF Contributions", "Grand Total"])
    cpf_table = Table("CPF", ["Month", "NRIC", "Employee Name", "Total CPF", "SDL", "Employer CPF", "Employee CPF", "Ordinary Wages", "Additional Wages", "Agency", "Agency Fund"])
    tables = [summary_table, cpf_table]
    row_start_pattern = re.compile(r'\d+.\s*[A-Z]{1}\d{7}[A-Z]{1}')  # E.g. 1. T0534907E
    month_pattern = re.compile(r'[A-Z]{3}\s*\d{4}')  # E.g. JAN 2026

    @classmethod
    def parse(cls, pdf):
        month = None
        summary_section = True
        total_cpf = 0
        interest = 0
        total_sdl = 0
        comm = 0
        mbmf = 0
        sinda = 0
        cdac = 0
        ecf = 0
        cur_row = None

        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')

            for line in lines:
                # Found month
                if month is None and (line.startswith("Contribution Details For") or line.startswith("Month Paid For")):
                    month_match = cls.month_pattern.search(line)
                    month_str = line[month_match.start():month_match.end()]
                    month = pd.to_datetime(month_str, format="%b %Y")

                # For summary table
                elif summary_section:
                    if "Total CPF Contributions" in line:
                        data = line.split(' ')
                        total_cpf = to_float(data[-1])

                    elif "CPF Late Payment Interest" in line:
                        data = line.split(' ')
                        interest = to_float(data[-1])

                    elif "Skills Development Levy (SDL)" in line:
                        data = line.split(' ')
                        total_sdl = to_float(data[-1])

                    elif "Donation to Community Chest" in line:
                        idx = line.find("Donor Count")
                        data = line[:idx].strip().split(' ')
                        comm = to_float(data[-1])

                    elif "Total MBMF Contributions" in line:
                        idx = line.find("Donor Count")
                        data = line[:idx].strip().split(' ')
                        mbmf = to_float(data[-1])

                    elif "Total SINDA Contributions" in line:
                        idx = line.find("Donor Count")
                        data = line[:idx].strip().split(' ')
                        sinda = to_float(data[-1])

                    elif "Total CDAC Contributions" in line:
                        idx = line.find("Donor Count")
                        data = line[:idx].strip().split(' ')
                        cdac = to_float(data[-1])

                    elif "Total ECF Contributions" in line:
                        idx = line.find("Donor Count")
                        data = line[:idx].strip().split(' ')
                        ecf = to_float(data[-1])

                    elif line.startswith("Grand Total"):
                        data = line.split(' ')
                        grand_total = to_float(data[-1])
                        row = [month, total_cpf, interest, total_sdl, comm, mbmf, sinda, cdac, ecf, grand_total]
                        cls.summary_table.rows.append(row)
                        summary_section = False

                # For details table
                elif cls.row_start_pattern.match(line):
                    if cur_row is not None:
                        cls.cpf_table.rows.append(cur_row)

                    data = line.split(' ')
                    _id = data[1]
                    name = ' '.join(data[2:-8])
                    total_cpf = to_float(data[-8])
                    sdl = to_float(data[-7])
                    employer_cpf = to_float(data[-6])
                    employee_cpf = to_float(data[-5])
                    ordinary_wages = to_float(data[-4])
                    additional_wages = to_float(data[-3])
                    agency = data[-2]
                    agency_fund = to_float(data[-1])

                    cur_row = [
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

                # End of page
                elif line.startswith("Copyright") or line.startswith("Total Amount"):
                    if cur_row is not None:
                        cls.cpf_table.rows.append(cur_row)

                    cur_row = None

                elif cur_row is not None:
                    cur_row[2] += ' ' + line # Name may span across multiple lines

        if cur_row is not None:
            cls.cpf_table.rows.append(cur_row)

        # Sort by month
        cls.summary_table.rows.sort(key=lambda row: row[0])
        cls.cpf_table.rows.sort(key=lambda row: row[0])


class CPFROPParser(Parser):
    file_header = "RECORD OF PAYMENT"
    summary_table = Table("CPF_Summary", ["Month", "CPF", "Late Payment Interest", "SDL", "MBMF", "SINDA", "CDAC", "Total"])
    cpf_table = Table("CPF", ["Month", "Name", "NRIC", "CPF"])
    tables = [summary_table, cpf_table]
    row_start_pattern = re.compile(r'[A-Z]X{4}\d{3}[A-Z]') # E.g. SXXXX482J, we use NRIC pattern to find row for a record
    month_pattern = re.compile(r'[A-Z]{3}\s*\d{4}')  # E.g. JAN 2026

    @classmethod
    def parse(cls, pdf):
        summary_section = True
        total_cpf = 0
        interest = 0
        sdl = 0
        mbmf = 0
        sinda = 0
        cdac = 0
        grand_total = 0
        month = None

        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')

            for line in lines:
                if summary_section:
                    if line.startswith("CPF Contribution"):
                        data = line.split(' ')
                        total_cpf = to_float(data[-1])

                    elif line.startswith("Late Payment Interest on CPF Contribution"):
                        data = line.split(' ')
                        interest = to_float(data[-1])

                    elif line.startswith("Skills Development Levy"):
                        data = line.split(' ')
                        sdl = to_float(data[-1])

                    elif line.startswith("Mosque Building & Mendaki Fund"):
                        data = line.split(' ')
                        mbmf = to_float(data[-1])

                    elif line.startswith("Singapore Indian Development Association"):
                        data = line.split(' ')
                        sinda = to_float(data[-1])

                    elif line.startswith("Chinese Development Assistance Council"):
                        data = line.split(' ')
                        cdac = to_float(data[-1])

                    # End of summary section
                    elif line.startswith("Total"):
                        data = line.split(' ')
                        grand_total = to_float(data[-1])
                        summary_section = False

                # Found month
                elif month is None and line.startswith("CPF Contributions Credited for the Month of"):
                    month_match = cls.month_pattern.search(line)
                    month_str = line[month_match.start():month_match.end()]
                    month = pd.to_datetime(month_str, format="%b %Y")
                    row = [month, total_cpf, interest, sdl, mbmf, sinda, cdac, grand_total]
                    cls.summary_table.rows.append(row)

                # For details table
                elif cls.row_start_pattern.search(line):
                    data = line.split(' ')
                    name = ' '.join(data[:-2])
                    NRIC = data[-2]
                    cpf = data[-1]

                    row = [month, name, NRIC, cpf]
                    cls.cpf_table.rows.append(row)

        # Sort by month
        cls.summary_table.rows.sort(key=lambda row: row[0])
        cls.cpf_table.rows.sort(key=lambda row: row[0])