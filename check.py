# import sqlite3

# conn = sqlite3.connect("students.db")
# cur = conn.cursor()

# cur.execute("SELECT username, password, role FROM users")
# rows = cur.fetchall()

# for row in rows:
#     print(f"Username: {row[0]}")
#     print(f"Password Hash: {row[1]}")
#     print(f"Role: {row[2]}")
#     print("-" * 30)

# conn.close()

# import sqlite3

# conn = sqlite3.connect("students.db")
# cur = conn.cursor()

# cur.execute("DELETE FROM users")
# conn.commit()
# conn.close()

# print("✅ Old users deleted.")

# import sqlite3
# import bcrypt
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Load credentials from .env
# DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME")
# DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD")
# DEFAULT_ADMIN_ROLE = os.getenv("DEFAULT_ADMIN_ROLE")

# if not DEFAULT_ADMIN_USERNAME or not DEFAULT_ADMIN_PASSWORD or not DEFAULT_ADMIN_ROLE:
#     raise Exception("⚠️ Admin credentials not set in .env")

# # Hash the password
# hashed_password = bcrypt.hashpw(DEFAULT_ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())

# # Save to DB
# conn = sqlite3.connect("students.db")
# cur = conn.cursor()

# cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
#             (DEFAULT_ADMIN_USERNAME, hashed_password.decode('utf-8'), DEFAULT_ADMIN_ROLE))
# conn.commit()
# conn.close()

# print(f"✅ Admin user seeded: {DEFAULT_ADMIN_USERNAME} / {DEFAULT_ADMIN_PASSWORD}")


