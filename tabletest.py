import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()
# check if dummy data can be inserted into database
cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (bob, 123456, bob@email.com)")
# check if null values can be inserted into database - tests pass if none of the three execute commands work
cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (, 123456, rob@email.com)")
cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (rob, , rob@email.com)")
cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (rob, 123456, )")
cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (rob, 123456, )")
# ensure unique fields only accept unique data - tests pass if none of the two commands work
cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (bob, 123456, alice@email.com)")
cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (alice, 123456, bob@email.com)")
# 
connection.commit()
connection.close()