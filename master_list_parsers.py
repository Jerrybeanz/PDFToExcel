import re
from master_list_tables import *


class BusinessProfileParser:
    def __init__(self):
        self.file_header = "ACCOUNTING AND CORPORATE REGULATORY AUTHORITY"

    def parse(self, pdf):
        company_row = []
        section = 0
        current_header_idx = -1
        current_field = None
        UEN = None
        activity = None
        next_row_shares = False

        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')

            for line in lines:
                # Section transitions
                if line == "Business Activities":
                    if current_field is not None:
                        company_row.append(current_field)
                    section = 1

                elif line == "Issued Share Capital":
                    section = 2

                elif line == "Officer(s)":
                    section = 3

                elif line == "Shareholder(s)":
                    section = 4

                # Stop parsing
                elif line == "Abbreviation":
                    break

                elif section == 0:
                    if current_header_idx == -1 and "Date:" in line:
                        data = line.split(' ')
                        date = ' '.join(data[-3:])
                        company_row.append(date)
                        current_header_idx += 1

                    else:
                        if line.startswith(companies_table.headers[current_header_idx+1]):
                            if current_field is not None:
                                company_row.append(current_field)

                            current_field = line.split(':')[1].strip()
                            current_header_idx += 1
                            if line.startswith("UEN"):
                                UEN = current_field

                        elif current_field is not None:
                            current_field += ' ' + line

                elif section == 1:
                    if line.startswith("Primary Activity") or line.startswith("Secondary Activity"):
                        activity = line.split(':')[1].strip()
                        if re.search(r'(\(\d{5}\))$', line):
                            company_row.append(activity)

                    elif re.search(r'(\(\d{5}\))$', line):
                        activity += line
                        company_row.append(activity)

                elif section == 2:
                    if line.startswith("Amount"):
                        next_row_shares = True

                    elif next_row_shares:
                        data = line.split(' ')
                        amount = int(data[0].replace(',', ''))
                        number_of_shares = int(data[1].replace(',', ''))
                        currency = ' '.join(data[2:4])
                        _type = data[4]
                        company_row.append(amount)
                        company_row.append(number_of_shares)
                        company_row.append(currency)
                        company_row.append(_type)
                        next_row_shares = False

                elif section == 3:
                    if re.match(r'([A-Z]+\s+){2,3}[A-Z]{1}\d{7}[A-Z]{1}', line):
                        _id_start_idx = re.search(r'[A-Z]{1}\d{7}[A-Z]{1}', line).start()
                        name = line[:_id_start_idx]
                        _id = line[_id_start_idx:_id_start_idx+10]
                        date_start_idx = re.search(r'\d{2}\s+[A-Z]{3}\s+\d{4}', line).start()
                        data = line[_id_start_idx+10:date_start_idx].split(' ')
                        nationality = data[0]
                        position = data[1]
                        date_of_appointment = line[date_start_idx:date_start_idx+11]

                        people_row = [name, _id, nationality]
                        people_table.table.append(people_row)

                        positions_row = [UEN, _id, position, date_of_appointment, None]
                        positions_table.table.append(positions_row)

                elif section == 4:
                    if re.match(r'([A-Z]+\s+){2,3}[A-Z]{1}\d{7}[A-Z]{1}', line):
                        _id_start_idx = re.search(r'[A-Z]{1}\d{7}[A-Z]{1}', line).start()
                        name = line[:_id_start_idx]
                        _id = line[_id_start_idx:_id_start_idx + 10]
                        data = line[_id_start_idx+10:].split(' ')
                        nationality = data[0]
                        share = int(data[1].replace(',', ''))
                        position = "SHAREHOLDER"

                        people_row = [name, _id, nationality]
                        people_table.table.append(people_row)

                        positions_row = [UEN, _id, position, None, share]
                        positions_table.table.append(positions_row)

        companies_table.table.append(company_row)