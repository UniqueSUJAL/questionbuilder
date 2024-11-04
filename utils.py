import sqlite3
import hashlib

def get_db_connection():
    conn = sqlite3.connect('your_database.db')
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()  # Simple hashing example
