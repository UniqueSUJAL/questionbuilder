import streamlit as st
from login import login
from registration import registration

def main():
    # Initialize the session state if it doesn't exist
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if "login_redirect" in st.session_state:
        # Clear the redirect flag
        del st.session_state["login_redirect"]
        # Redirect to login
        main()  # This should be your function or logic to display the login page
        return
    # Check if user is already logged in
    if st.session_state.logged_in ==True:
        # Hide the sidebar when the user is logged in
        st.sidebar.empty()  # Remove all contents from the sidebar
        st.title("Welcome!")  # You can customize this title or add more content for logged-in users
        # Display any other user-specific content or features here
    else:
        
        st.sidebar.title("🔍 Navigation")
        choice = st.sidebar.selectbox("Go to", ["🔑 Login", "📝 Registration"])

        if choice == "🔑 Login":
            if login():  # Assuming login() returns True if login is successful
                st.session_state.logged_in = True  # Set logged_in state to True
                st.experimental_rerun()  # Refresh the app to update the sidebar
        elif choice == "📝 Registration":
            registration()

if __name__ == '__main__':
    main()
