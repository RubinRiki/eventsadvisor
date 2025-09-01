from dotenv import load_dotenv
import os, pyodbc

load_dotenv()
conn = pyodbc.connect(os.getenv("DB_URL"), autocommit=True)
cur = conn.cursor()

cur.execute("""
SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME='Users'
ORDER BY ORDINAL_POSITION;
""")

print("Columns in Users:")
for row in cur.fetchall():
    print(f"- {row.COLUMN_NAME} ({row.DATA_TYPE}) [schema={row.TABLE_SCHEMA}]")
