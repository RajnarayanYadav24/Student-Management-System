import sqlite3

conn = sqlite3.connect("students.db")
cur = conn.cursor()

cur.execute("SELECT username, password, role FROM users")
rows = cur.fetchall()

for row in rows:
    print(f"Username: {row[0]}")
    print(f"Password Hash: {row[1]}")
    print(f"Role: {row[2]}")
    print("-" * 30)