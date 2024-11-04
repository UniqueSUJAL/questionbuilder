import streamlit as st
import sqlite3
import re
from database_setup import get_db_connection, hash_password

# Function to validate email format
def validate_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

# Function to validate phone number format
def validate_phone(phone):
    regex = r'^\d{10}$'
    return re.match(regex, phone) is not None

# Registration Page
def registration():
    # Adding custom CSS
    st.markdown(
        """
        <style>
            .registration-title {
                font-size: 2rem;
                color: #4A90E2;
                text-align: center;
                margin-bottom: 20px;
            }
            .stButton > button {
                background-color: #4CAF50;
                color: white;
                font-size: 1rem;
                border-radius: 5px;
            }
            .stTextInput, .stSelectbox {
                margin: 10px 0;
            }
            .error {
                color: red;
                font-weight: bold;
            }
            .success {
                color: green;
                font-weight: bold;
            }
          .icon-label {
        font-size: 22px;  /* Adjust font size to make icons larger */
        margin-right: 10px;
    }
    .input-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 15px;
    }
    .icon-label {
        color: #4CAF50;  /* Optional: change icon color */
    }


        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<h1 class="registration-title">Create your profile</h1>', unsafe_allow_html=True)

    # Create a form
    with st.form(key='registration_form'):
        st.markdown('<div class="input-container"><span class="icon-label">👤</span>' +
                '<label for="name_input" class="icon-label">Name</label></div>', unsafe_allow_html=True)
        name = st.text_input("Name", key="name_input", label_visibility="collapsed")
    
        st.markdown('<div class="input-container"><span class="icon-label">📧</span>' +
                '<label for="email_input" class="icon-label">Email</label></div>', unsafe_allow_html=True)
        email = st.text_input("Email", key="email_input", label_visibility="collapsed")
    
        st.markdown('<div class="input-container"><span class="icon-label">📞</span>' +
                '<label for="phone_input" class="icon-label">Phone Number</label></div>', unsafe_allow_html=True)
        phone = st.text_input("Phone Number", key="phone_input", label_visibility="collapsed")
    
        st.markdown('<div class="input-container"><span class="icon-label">🧑‍💼</span>' +
                '<label for="role_input" class="icon-label">Role</label></div>', unsafe_allow_html=True)
        role = st.selectbox("Role", ['trainer', 'employee'], key="role_input", label_visibility="collapsed")
    
        st.markdown('<div class="input-container"><span class="icon-label">🔒</span>' +
                '<label for="password_input" class="icon-label">Password</label></div>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", key="password_input", label_visibility="collapsed")
    
        st.markdown('<div class="input-container"><span class="icon-label">🔑</span>' +
                '<label for="confirm_password_input" class="icon-label">Confirm Password</label></div>', unsafe_allow_html=True)
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password_input", label_visibility="collapsed")
    
        submit_button = st.form_submit_button("Register")
    
    if submit_button:
        if not name or not email or not phone or not password:
            st.markdown('<p class="error">All fields are required.</p>', unsafe_allow_html=True)
        elif password != confirm_password:
            st.markdown('<p class="error">Passwords do not match!</p>', unsafe_allow_html=True)
        elif not validate_email(email):
            st.markdown('<p class="error">Invalid email! Please use a valid Gmail address.</p>', unsafe_allow_html=True)
        elif not validate_phone(phone):
            st.markdown('<p class="error">Invalid phone number! It should be 10 digits.</p>', unsafe_allow_html=True)
        else:
            # Check if the email already exists
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            existing_user = cursor.fetchone()
            conn.close()

            if existing_user:
                st.markdown('<p class="error">User with this email already exists!</p>', unsafe_allow_html=True)
            else:
                hashed_password = hash_password(password)
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(""" 
                        INSERT INTO users (name, email, password, role, phone_number) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (name, email, hashed_password, role, phone))
                    conn.commit()
                    conn.close()
                    st.markdown(f'<p class="success">Registration successful! Welcome, {name}.</p>', unsafe_allow_html=True)
                except sqlite3.Error as e:
                    st.markdown(f'<p class="error">An error occurred: {str(e)}</p>', unsafe_allow_html=True)

