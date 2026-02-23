import sqlite3
import pandas as pd
from pandas import Timestamp
from datetime import datetime, date


def upsert_from_table(table, df, database_path):
    # Register adapter once at the start of your script
    sqlite3.register_adapter(Timestamp, lambda ts: ts.strftime('%Y-%m-%d'))
    sqlite3.register_adapter(datetime, lambda dt: dt.strftime('%Y-%m-%d'))
    sqlite3.register_adapter(date, lambda d: d.strftime('%Y-%m-%d'))
    sqlite3.register_adapter(type(pd.NaT), lambda x: None)

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Prepare SQL statements
        placeholders = ', '.join(['?' for _ in table.headers])
        set_clause = ', '.join([f'"{col}"=excluded."{col}"' for col in table.headers if col not in table.primary_keys])

        # SQLite UPSERT syntax
        upsert_sql = f"""
        INSERT INTO {table.name} ({', '.join(f'"{column}"' for column in table.headers)})
        VALUES ({placeholders})
        ON CONFLICT({', '.join(f'"{key}"' for key in table.primary_keys)}) 
        DO UPDATE SET {set_clause};
        """
        print(upsert_sql)

        for _, row in df.iterrows():
            cursor.execute(upsert_sql, tuple(row))

        conn.commit()

    print(f"✅ Processed {len(table.table)} records")