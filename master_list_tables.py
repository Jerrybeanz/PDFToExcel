class Table:
    def __init__(self, name):
        self.name = name
        self.definition = ""
        self.headers = []
        self.table = []
        self.primary_keys = []


companies_table = Table("Companies")
companies_table.definition = \
"""
CREATE TABLE IF NOT EXISTS Companies (
"Date Updated" DATE,
 "Name of Company" TEXT,
 "Former Name" TEXT,
 "Date of Change of Name" DATE,
 "UEN" TEXT,
 "Incorporation Date" DATE,
 "Company Type" TEXT,
"Status of Company" TEXT,
"Status Date" DATE,
"Registered Office Address" TEXT,
"Date of Address" DATE,
"Date of Last AGM" DATE,
"Date of Last AR" DATE,
"FYE As At Date of Last AR" DATE,
"Primary Activity" TEXT,
"Secondary Activity" TEXT,
"Issued Share Amount" INTEGER,
"Issued Number of Shares" INTEGER,
"Issued Share Currency" TEXT,
"Issued Share Type" TEXT,
"Paid-Up Share Amount" INTEGER,
"Paid-Up Number of Shares" INTEGER,
"Paid-Up Share Currency" TEXT,
"Paid-Up Share Type" TEXT,
PRIMARY KEY("UEN")
);
"""
companies_table.headers = \
["Date Updated", "Name of Company", "Former Name", "Date of Change of Name", "UEN", "Incorporation Date", "Company Type",
   "Status of Company", "Status Date", "Registered Office Address", "Date of Address", "Date of Last AGM",
   "Date of Last AR", "FYE As At Date of Last AR", "Primary Activity", "Secondary Activity",
   "Issued Share Amount", "Issued Number of Shares", "Issued Share Currency", "Issued Share Type",
   "Paid-Up Share Amount", "Paid-Up Number of Shares", "Paid-Up Share Currency", "Paid-Up Share Type"]
companies_table.primary_keys = ["UEN"]

people_table = Table("People")
people_table.definition = \
"""
CREATE TABLE IF NOT EXISTS "People" (
	"Name"	TEXT,
	"NRIC/FIN"	TEXT,
	"Nationality"	TEXT,
	PRIMARY KEY("NRIC/FIN")
);
"""
people_table.headers = ["Name", "NRIC/FIN", "Nationality"]
people_table.primary_keys = ["NRIC/FIN"]

positions_table = Table("Positions")
positions_table.definition = """
CREATE TABLE IF NOT EXISTS "Positions" (
	"UEN"	TEXT,
	"NRIC/FIN"	TEXT,
	"Position"	TEXT,
	"Date of Appointment"	DATE,
	"Shares"	INTEGER,
	PRIMARY KEY("UEN", "NRIC/FIN", "Position"),
	FOREIGN KEY("UEN") REFERENCES "Companies"("UEN"),
	FOREIGN KEY("NRIC/FIN") REFERENCES "People"("NRIC/FIN")
);
"""
positions_table.headers = ["UEN", "NRIC/FIN",  "Position", "Date of Appointment", "Shares"]
positions_table.primary_keys = ["UEN", "NRIC/FIN", "Position"]

master_list_tables = {table.name: table for table in (companies_table, people_table, positions_table)}