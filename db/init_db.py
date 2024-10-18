import sqlite3

conn = sqlite3.connect('./db/data.db')

with open("./db/schemas.sql") as file:
    conn.executescript(file.read())

conn.commit()
conn.close()