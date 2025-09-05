import sqlite3

# Connect to your database
conn = sqlite3.connect("auth.db")
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# Fetch users (if you have a 'users' table)
cursor.execute("SELECT * FROM users;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
