import streamlit as st
from database_setup import get_db_connection, hash_password
from dashboard import display_dashboard

def login():
    conn = get_db_connection()
    cursor = conn.cursor()

    # If the user is already logged in, go directly to the dashboard
    if 'user' in st.session_state:
        display_dashboard(st.session_state.user)
        return

    # Page Styling
    st.markdown(
        """
        <style>
            body {
                background-color: #c0c4cc;  /* Set a solid background color */
                background: linear-gradient(135deg, white, #c0c4cc); /* Gradient overlay */
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh;  
                margin: 0;  
            }
            .login-container {
                text-align: center; 
                color:Black; 
                background-color: #f9f9f9;  
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0, 0, 1, 0.1);
                width: 400px;  /* Fixed width for centering */
            }
            .login-title {
                font-size: 2em;
                font-weight: 600;  /* Corrected weight */
                margin-bottom: 5px;
                
                text-align: center;
                color:white;
            }
            .image-container {
                display: flex;
                justify-content: center;  
                margin: 5px 0;  
            }
            .stTextInput, .stButton {
                margin: 7px 0;  /* Centering elements */
                width: 100%; 
                
                 /* Full width */
            }
  
            .stImage{
           justify-content: center;}

           
        </style>
        """,
        unsafe_allow_html=True
    )

    # Using st.form for structured input
    with st.form(key="login_form"):
        st.markdown('<div class="login-title">LOGIN</div>', unsafe_allow_html=True)

        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image("user-login-icon.png", width=100)  # Adjust the path as necessary
        st.markdown('</div>', unsafe_allow_html=True)

        # Email input
        email = st.text_input("📧 Email", key="email", placeholder="Enter your email", help="Enter your registered email")

        # Password input
        password = st.text_input("🔑 Password", type="password", key="password", placeholder="Enter your password")

        # Submit button
        submit_button = st.form_submit_button(label="LOGIN")

        st.markdown('</div>', unsafe_allow_html=True)  # Close the login-container div

    # Check if the form is submitted
    if submit_button:
        hashed_password = hash_password(password)
        cursor.execute("""SELECT * FROM users WHERE email = ? AND password = ? AND status = 'approved'""",
                       (email, hashed_password))
        user = cursor.fetchone()

        if user:
            st.session_state.user = user
            st.success(f"Welcome {user[1]}!")  # Assuming user[1] is the name
        else:
            st.error("Invalid credentials or account not approved.")

    conn.close()

if __name__ == "__main__":
    login()
