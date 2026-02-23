import sys
import sqlite3
from master_list_tables import *


def create_database(database_path=None):
    if database_path is None:
        # Running as exe file from Excel VBA
        if getattr(sys, 'frozen', False):
            database_path = sys.argv[1]
        else:
            database_path = "MasterList.db"

    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()
        cursor.execute(companies_table.definition)
        cursor.execute(people_table.definition)
        cursor.execute(positions_table.definition)
        connection.commit()


if __name__ == "__main__":
    create_database()