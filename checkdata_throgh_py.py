import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('question_builder.db')
cursor = conn.cursor()

# Query to fetch all users
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

# Display user data
print("\nUsers Table:")
print("User ID | Name          | Email                | Role   | Phone Number | Password  | Status")
print("-------------------------------------------------------------------------------------------")
for user in users:
    print(f"{user[0]:<8} | {user[1]:<12} | {user[2]:<20} | {user[4]:<6} | {user[5]:<12} | {user[3]:<9} | {user[6]}")

# # Query to fetch all questions
# cursor.execute("SELECT * FROM questions1")
# questions = cursor.fetchall()

# Display questions data
# print("\nQuestions Table:")
# print("ID | Question                    | Description               | Type      | Difficulty | Subject")
# print("--------------------------------------------------------------------------------------------")
# for question in questions:
#     print(f"{question[0]:<2} | {question[1]:<25} | {question[2]:<25} | {question[3]:<10} | {question[4]:<10} | {question[5]}")

# # Close the database connection
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# Print the tables
# print(tables)


conn.close()
