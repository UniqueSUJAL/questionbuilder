import sqlite3
from hashlib import sha256
import streamlit as st 
import pandas as pd
import numpy as np

DATABASE_NAME = 'question_builder.db'

# ---------------------------------------------
# Database Connection and Setup Functions
# ---------------------------------------------
def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    return sqlite3.connect(DATABASE_NAME)

def hash_password(password):
    """Hash the password using SHA-256."""
    return sha256(password.encode()).hexdigest()

def create_tables(cursor):
    """Create the required tables if they do not already exist."""
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin', 'trainer', 'employee')),
        phone_number TEXT,
        status TEXT CHECK(status IN ('approved', 'pending')) DEFAULT 'pending'
    );

    CREATE TABLE IF NOT EXISTS questions1 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        description TEXT,
        question_type TEXT,
        difficulty_level TEXT,
        subject TEXT
    );

    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT CHECK(status IN ('seen', 'pending')) DEFAULT 'pending',
        
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES questions1(id) ON DELETE CASCADE
    );
    """)

def insert_default_admin(cursor):
    """Insert a default admin user if no admin exists with user_id = 1."""
    cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = 1")
    user_count = cursor.fetchone()[0]

    if user_count == 0:
        default_admin = {
            'user_id': 1,
            'name': 'Admin User 1',
            'email': 'admin1@example.com',
            'password': 'admin123',
            'role': 'admin',
            'phone_number': '1234567890'
        }

        cursor.execute("""
            INSERT INTO users (user_id, name, email, password, role, phone_number, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (default_admin['user_id'], default_admin['name'], default_admin['email'],
              hash_password(default_admin['password']), default_admin['role'], 
              default_admin['phone_number'], 'approved'))

        print("Default admin user created successfully with user_id = 1!")

def setup_database():
    """Set up the database by creating tables and inserting a default admin if necessary."""
    conn = get_db_connection()
    cursor = conn.cursor()
    create_tables(cursor)
    insert_default_admin(cursor)
    conn.commit()
    conn.close()
    print("Database setup completed successfully!")

# ---------------------------------------------
# Question Management Functions
# ---------------------------------------------
def insert_question(question, description, question_type, difficulty_level, subject):
    """Insert a new question into the database, avoiding duplicates."""
    conn = get_db_connection()
    cursor = conn.cursor()

    subject = subject.lower()  # Store subject as lowercase for consistency

    cursor.execute("""
        SELECT * FROM questions1 
        WHERE question = ? AND LOWER(subject) = ?
    """, (question, subject))
    existing_question = cursor.fetchone()

    if existing_question:
        if (existing_question[3] == question_type) and (existing_question[4] == difficulty_level):
            print(f"Duplicate question found: {existing_question[1]} (Type: {question_type}, Level: {difficulty_level})")
        else:
            cursor.execute("""
                INSERT INTO questions1 (question, description, question_type, difficulty_level, subject)
                VALUES (?, ?, ?, ?, ?)
            """, (question, description, question_type, difficulty_level, subject))
            conn.commit()
            print("Question inserted successfully with a different type or difficulty level.")
    else:
        cursor.execute("""
            INSERT INTO questions1 (question, description, question_type, difficulty_level, subject)
            VALUES (?, ?, ?, ?, ?)
        """, (question, description, question_type, difficulty_level, subject))
        conn.commit()
        print("Question inserted successfully.")

    conn.close()

def delete_question(question_id):
    """Delete a question by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions1 WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()
    print(f"Question with ID {question_id} deleted successfully.")

def update_question(question_id, question, subject, question_type, difficulty_level):
    """Update an existing question."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if is_duplicate_question(question, subject, question_type, difficulty_level, question_id):
        return "Duplicate question detected. Update aborted."

    cursor.execute("""
        UPDATE questions1 
        SET question = ?, subject = ?, question_type = ?, difficulty_level = ? 
        WHERE id = ?
    """, (question, subject, question_type, difficulty_level, question_id))
    conn.commit()
    conn.close()
    return "Question updated successfully."

def is_duplicate_question(question, subject, question_type, difficulty_level, question_id):
    """Check if a similar question already exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM questions1
        WHERE question = ? AND subject = ? AND question_type = ? 
        AND difficulty_level = ? AND id != ?
    """, (question, subject, question_type, difficulty_level, question_id))
    duplicate = cursor.fetchone() is not None
    conn.close()
    return duplicate

# ---------------------------------------------
# Feedback Management Functions
# ---------------------------------------------
def get_feedback_summary(subject):
    """Fetch average rating, feedback count, and detailed feedback for a specific subject."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to get average rating, feedback count, and detailed feedback by subject
    cursor.execute("""
        SELECT 
            
            u.name AS user_name,
            f.comment,
            q.question AS question_text,
            q.subject,
            q.question_type AS type,
            q.difficulty_level AS level,
            f.status,
            f.id AS feedback_id,  -- Retrieve feedback id
            q.id AS question_id,  -- Retrieve question id
            u.email,
            f.rating
        FROM 
            feedback f
        JOIN 
            users u ON f.user_id = u.user_id
        JOIN 
            questions1 q ON q.id = f.question_id
        WHERE 
            f.subject = ?
        GROUP BY 
            f.id, u.name, f.comment, q.question, q.subject, q.question_type, q.difficulty_level, 
            f.status, q.id, u.email, f.rating
    """, (subject,))

    results = cursor.fetchall()
    conn.close()

    # Prepare summary details
    avg_rating = results[0][0] if results else 0
    feedback_count = results[0][1] if results else 0

    feedback_details = []
    for row in results:
        feedback_details.append({
            
            "comment": row[3],
            "question_text": row[4],
            "subject": row[5],
            "type": row[6],
            "level": row[7],
            "status": row[8],
            "feedback_id": row[9],
            "question_id": row[10],
            "email": row[11],
            "rating": row[12]
        })

    return avg_rating, feedback_count, feedback_details

def get_general_feedback_summary():
    """Fetch all general feedback including user names and comments."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to get general feedback
    cursor.execute("""
        SELECT 
            
            u.name AS user_name,
            f.rating,
            f.comment,
            f.created_at,
            f.status,
            f.id,
            u.email

        FROM 
            feedback f
        JOIN 
            users u ON f.user_id = u.user_id
        WHERE 
            f.question_id IS NULL
    """)
    
    results = cursor.fetchall()
    conn.close()

    # Prepare feedback details
    general_feedback_details = []
    for row in results:
        general_feedback_details.append({
            "user_name": row[0],
            "rating": row[1],
            "comment": row[2],
            "created_at": row[3],
            "status": row[4],
            "id": row[5],
            "email":row[6]
        })
    
    return general_feedback_details

def fetch_questions():
    """Fetch questions from the database for the dropdown."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, question FROM questions1")  # Fixed missing comma
    questions = cursor.fetchall()
    conn.close()
    return questions

def submit_feedback(user_id, question_id, rating, comment):
    """Submit feedback to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (user_id, question_id, rating, comment)
        VALUES (?, ?, ?, ?)
    """, (user_id, question_id, rating, comment))
    conn.commit()
    conn.close()
    
# ---------------------------------------------
# Utility Functions
# ---------------------------------------------
def get_unique_subjects():
    """Fetch all unique subjects from the questions1 table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT subject FROM questions1")
    subjects = [row[0] for row in cursor.fetchall()]
    conn.close()
    return subjects

def get_filtered_questions(subject=None, question_type=None, difficulty_level=None):
    """Fetch filtered questions based on subject, type, and difficulty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM questions1 WHERE 1=1"
    params = []
    
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if question_type:
        query += " AND question_type = ?"
        params.append(question_type)
    if difficulty_level:
        query += " AND difficulty_level = ?"
        params.append(difficulty_level)

    cursor.execute(query, params)
    questions = cursor.fetchall()
    conn.close()
    return questions


def update_feedback_status(feedback_id, new_status):
    """Update the status of feedback based on feedback ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ensure the new status is valid
    if new_status not in ['seen', 'pending']:
        raise ValueError("Invalid status. Must be 'seen' or 'pending'.")

    cursor.execute("""
        UPDATE feedback 
        SET status = ? 
        WHERE id = ?
    """, (new_status, feedback_id))
    conn.commit()
    conn.close()
    print(f"Feedback status for ID {feedback_id} updated to '{new_status}'.")



def get_subjects():
    """Retrieve a list of unique subjects from the feedback table."""
    conn =get_db_connection()  # Update with your database path
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT q.subject
        FROM feedback f
        JOIN questions1 q ON f.question_id = q.id
    """)
    subjects = [row[0] for row in cursor.fetchall()]
    conn.close()
    return subjects


#-------------------------------------------------
# Graph Admin Dashboard
#-------------------------------------------------
def get_user_counts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    results = cursor.fetchall()
    conn.close()
    return pd.DataFrame(results, columns=["Role", "Count"])

def get_question_counts():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count by subject
    cursor.execute("SELECT subject, COUNT(*) FROM questions1 GROUP BY subject")
    subject_counts = cursor.fetchall()
    
    # Count by question type
    cursor.execute("SELECT question_type, COUNT(*) FROM questions1 GROUP BY question_type")
    type_counts = cursor.fetchall()
    
    # Count by difficulty level and subject
    cursor.execute("SELECT subject, difficulty_level, COUNT(*) FROM questions1 GROUP BY subject, difficulty_level")
    difficulty_counts = cursor.fetchall()
    
    conn.close()
    
    return {
        "types": pd.DataFrame(type_counts, columns=["Type","Count"]),
        "subjects": pd.DataFrame(subject_counts, columns=["Subject", "Count"]),
        "difficulty_levels": pd.DataFrame(difficulty_counts, columns=["Subject", "Difficulty Level", "Count"]),
    }


def get_question_counts1():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count by subject
    cursor.execute("SELECT subject, COUNT(*) FROM questions1 GROUP BY subject")
    subject_counts = cursor.fetchall()
    
    # Count by question type
    cursor.execute("SELECT question_type, COUNT(*) FROM questions1 GROUP BY question_type")
    type_counts = cursor.fetchall()
    
    # Count by difficulty level and question type
    cursor.execute("SELECT difficulty_level, question_type, COUNT(*) FROM questions1 GROUP BY difficulty_level, question_type")
    difficulty_counts = cursor.fetchall()
    
    conn.close()
    
    return {
        "subjects": pd.DataFrame(subject_counts, columns=["Subject", "Count"]),
        "types": pd.DataFrame(type_counts, columns=["Type", "Count"]),
        "difficulty_levels": pd.DataFrame(difficulty_counts, columns=["Difficulty Level", "Type", "Count"]),
    }


def get_pending_feedback_counts():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM feedback WHERE status = 'pending'")
    pending_feedback = cursor.fetchone()[0]
    conn.close()
    return pending_feedback

def get_pending_user_approvals():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'pending'")
    pending_approvals = cursor.fetchone()[0]
    conn.close()
    return pending_approvals


#===========================================
#Admin approvral
#============================================
def approve_user(email):
    """Approve a user by updating their status in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Update the user status to 'approved'
        cursor.execute("UPDATE users SET status = 'approved' WHERE email = %s", (email,))
        conn.commit()

        # Check if any row was updated
        if cursor.rowcount > 0:
            st.success(f"User {email} approved successfully.")
        else:
            st.warning(f"No user found with email: {email}.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        conn.close()




# ---------------------------------------------
# Main Streamlit App Logic
# ---------------------------------------------
if __name__ == "__main__":
    # Initialize the database
    setup_database()
    
    # # Streamlit App Interface
    # st.title("Automated Question Builder Application")
    
    # # Example user registration for testing
    # st.header("Register User")
    # name = st.text_input("Name")
    # email = st.text_input("Email")
    # password = st.text_input("Password", type="password")
    # phone_number = st.text_input("Phone Number")
    
    # if st.button("Register"):
    #     conn = get_db_connection()
    #     cursor = conn.cursor()
    #     try:
    #         cursor.execute("""
    #             INSERT INTO users (name, email, password, role, phone_number, status)
    #             VALUES (?, ?, ?, 'employee', ?, 'pending')
    #         """, (name, email, hash_password(password), phone_number))
    #         conn.commit()
    #         st.success("User registered successfully!")
    #     except sqlite3.IntegrityError:
    #         st.error("Email already exists. Please use a different email.")
    #     finally:
    #         conn.close()

    # # Example feedback submission
    # st.header("Submit Feedback")
    # user_id = 1  # Assuming user ID for feedback submission
    # questions = fetch_questions()
    # question_id = st.selectbox("Select Question", [q[0] for q in questions], format_func=lambda x: next(q[1] for q in questions if q[0] == x))
    # rating = st.slider("Rating", 1, 5)
    # comment = st.text_area("Comment")
    
    # if st.button("Submit Feedback"):
    #     submit_feedback(user_id, question_id, rating, comment)
    
    # # Fetch and display questions
    # st.header("All Questions")
    # questions = fetch_questions()
    # for question in questions:
    #     st.write(f"ID: {question[0]}, Question: {question[1]}, Type: {question[3]}, Level: {question[4]}, Subject: {question[5]}")

    # # Summary of feedback for a specific question
    # st.header("Feedback Summary for a Question")
    # question_id = st.selectbox("Select Question for Feedback Summary", [q[0] for q in questions], format_func=lambda x: next(q[1] for q in questions if q[0] == x))
    # if st.button("Get Feedback Summary"):
    #     avg_rating, feedback_count, feedback_details = get_feedback_summary(question_id)
    #     st.write(f"Average Rating: {avg_rating}, Feedback Count: {feedback_count}")
    #     for detail in feedback_details:
    #         st.write(f"{detail['user_name']} - {detail['comment']} (Status: {detail['status']})")
