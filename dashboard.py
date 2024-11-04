import streamlit as st
from database_setup import (
    get_db_connection,
    hash_password,
    get_filtered_questions,
    fetch_questions,
    submit_feedback,
    get_unique_subjects,
    get_feedback_summary,
    get_general_feedback_summary,
    update_feedback_status,
    get_subjects,
    get_user_counts,
    get_question_counts,
    get_question_counts1,
    get_pending_feedback_counts,
    get_pending_user_approvals,
    
   
)
import plotly.express as px
import plotly.graph_objects as go
from question_genrator import question_generator_app
from fetch import display_questions_ui  # Importing question bank UI function
from edit_update_question import edit_questions_table
import pandas as pd 
from feedback import feedback_form, display_general_feedback  # Importing feedback functions
from io import BytesIO
from datetime import datetime
from fpdf import FPDF


def generate_pdf_report(figures, summary_data, filename):
    """Generate a PDF report containing figures and summary data."""
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, f"Dashboard Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
    pdf.ln(10)
    
    # Add summary data
    pdf.set_font("Arial", size=10)
    for key, value in summary_data.items():
        pdf.cell(200, 10, f"{key}: {value}", 0, 1)
    
    # Add figures
    for fig_name, fig in figures.items():
        buffer = BytesIO()
        fig.write_image(buffer, format="PNG")
        buffer.seek(0)
        pdf.image(buffer, x=10, w=190)
        pdf.ln(10)
    
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

def generate_csv_report(dataframes, filename):
    """Generate a CSV report from dataframes."""
    csv_output = BytesIO()
    with pd.ExcelWriter(csv_output, engine="xlsxwriter") as writer:
        for name, df in dataframes.items():
            df.to_excel(writer, sheet_name=name)
    csv_output.seek(0)
    return csv_output


#==========================================
#Display Dashboard
#==========================================
def display_dashboard(user):

    st.markdown(
    """
    <style>
    .sidebar-title {
        font-size: 24px;
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: bold;
        color: #4CAF50; /* Optional: change color */
        margin-bottom: 20px;
    }
    .logout-button {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 20px;
        color: white;
        background-color: #FF5733; /* Optional: change button color */
        padding: 8px 16px;
        border-radius: 8px;
        text-align: center;
    }
    .logout-button:hover {
        background-color: #FF2D00; /* Optional: hover effect */
    }
    </style>
    """,
    unsafe_allow_html=True
)
    
    st.sidebar.markdown('<div class="sidebar-title">📊 Dashboard</div>', unsafe_allow_html=True)


    if st.sidebar.button("🚪 Logout"):
        
        logout()


    role = user[4]  # Assuming user role is stored in user[4]
    
# Assuming user role is stored in user[4]
    

    if role == 'admin':
        page = st.sidebar.selectbox("Choose a page:", ["Home", "Create Questions", "Question Bank", "Edit Question Bank", "Feedback Summary"])

        if page == "Home":
            st.title(f"Welcome {user[1]}")
            st.markdown("""
        <style>
        body {
            background-color: #1e1e1e;  /* Dark background */
            color: #f5f5f5;  /* Light text color */
        }
        .reportview-container {
            background-color: #1e1e1e;
        }
        .sidebar .sidebar-content {
            background-color: #252526;  /* Sidebar color */
            color: white;
        }
        .stTitle {
            font-size: 2em;
            color: #4b8be1;  /* Accent color */
            text-align: center;
            margin-top: 20px;
        }
        .stSubheader {
            color: #4b8be1;
        }
        .card {
            background-color: #2a2a2a;  /* Card background */
            border-radius: 10px;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.5);
            padding: 10px;
            bottom-margin: 80px;
            display:center;
            flex-direction: column;
            align-items: center;
            text-align: center;
            height: 4px;
        }
        .header {
            text-align: center;
            font-size: 1.5em;
            margin-bottom: 15px;
            color: #f5f5f5;
        }
        .chart-title {
            margin-bottom:-63px;
            font-weight: bold;
            text-align:center;
            color: #4b8be1;
            height: 100px;
           
        }
        .progress-circle {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            border: 50px solid #4b8be1;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 1.5em;
            color: #4b8be1;
            background-color: #2a2a2a;  /* Dark background for circle */
            margin:0px;
        }
        .pending-counts {
            
            justify-content:center;
            color: #f5f5f5;  /* Light text for counts */
            font-size: 1.2em;
        }
        /* Style for column borders */
        .stColumn {
            border: 2px solid #4b8be1; /* Blue border color */
            padding:10px;
            border-radius: 8px;
            height:35vw;
            width:50vw;
            
        }
    </style>
""", unsafe_allow_html=True)

# Page selection
            

            
    # Fetch data for graphs
            user_counts = get_user_counts()
            user_df = pd.DataFrame(user_counts)

            question_counts = get_question_counts()
            types_df = question_counts.get("types")
            difficulty_df = question_counts["difficulty_levels"]

            st.subheader("📊Dashboard Overview")

    # Create the first row with 3 charts (Doughnut, Pie, Heatmap)
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown('<div class="chart-title">User Roles Distribution</div>', unsafe_allow_html=True)
                fig_users = go.Figure(data=[go.Pie(labels=user_df["Role"], values=user_df["Count"], hole=.5)])
                fig_users.update_traces(textinfo="percent+label", marker=dict(colors=['#4b8be1', '#f09c20', '#dd1c1c']))
                fig_users.update_layout(width=450, height=450)
                st.plotly_chart(fig_users, use_container_width=True)

            with col2:
                st.markdown('<div class="chart-title">Distribution of Question Types</div>', unsafe_allow_html=True)
                fig_types = px.pie(types_df, names="Type", values="Count", color_discrete_sequence=px.colors.sequential.RdBu)
                fig_types.update_traces(textinfo="percent+label")
                fig_types.update_layout(width=450, height=450)
                st.plotly_chart(fig_types, use_container_width=True)

            with col3:
                st.markdown('<div class="chart-title">Question Difficulty Levels</div>', unsafe_allow_html=True)
                fig_difficulty_levels = px.density_heatmap(
                difficulty_df,
                x="Difficulty Level",
                y="Difficulty Level",
                z="Count",
                color_continuous_scale="Blues",
            )
                fig_difficulty_levels.update_layout(
                width=350,
                height=350,
                xaxis_title="Difficulty Level",
                yaxis_title="",
                yaxis_visible=False
                )
                st.plotly_chart(fig_difficulty_levels, use_container_width=True)

    # Create the second row with 2 sections (Stacked Bar Chart and Pending Counts)
            col4, col5 = st.columns(2)

            with col4:
                st.markdown('<div class="chart-title">Subject and Difficulty Level</div>', unsafe_allow_html=True)
                fig_difficulty = px.bar(
                difficulty_df,
                y="Subject",
                x="Count",
                color="Difficulty Level",
                orientation="h",
                )
                fig_difficulty.update_layout(barmode="stack", yaxis_title="Subject", xaxis_title="Count", plot_bgcolor='rgba(0, 0, 0, 0)')
                st.plotly_chart(fig_difficulty, use_container_width=True)

            with col5:
                pending_feedbacks = get_pending_feedback_counts()
                pending_approvals = get_pending_user_approvals()
                st.markdown('<div class="chart-title">Pending Counts</div>', unsafe_allow_html=True)
                st.markdown(f"<div class='pending-counts'>Pending Feedbacks: {pending_feedbacks}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='pending-counts'>Pending User Approvals: {pending_approvals}</div>", unsafe_allow_html=True)


    
    elif role == 'trainer':

        page = st.sidebar.selectbox("Choose a page:", ["Home","Create Questions", "Question Bank", "Feedback Form"])
        if page == "Home":
            st.title(f"Welcome {user[1]}")
            st.write(f"{user[4]}")
# 2. Total Number of Questions by Subject and Difficulty Level
            question_counts = get_question_counts()  
            difficulty_df = question_counts["difficulty_levels"]

            st.subheader("Question set")

# Stacked Bar Chart for Questions by Subject with Difficulty Levels as Stacks
            fig_difficulty = px.bar(
                difficulty_df,
                y="Subject",
                x="Count",
                color="Difficulty Level",
                orientation="h",  # Horizontal orientation
                title="Questions by Subject and Difficulty Level",
            )
            fig_difficulty.update_layout(barmode="stack", yaxis_title="Subject", xaxis_title="Count")
            st.plotly_chart(fig_difficulty, use_container_width=True)
            # 4. Questions by Difficulty Level: Separate Pie Chart
            st.write("Questions by Difficulty Level")
            fig_difficulty_levels = px.pie(difficulty_df, names="Difficulty Level", values="Count", title="Distribution of Question Difficulty Levels")
            fig_difficulty_levels.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_difficulty_levels, use_container_width=True)
    
    elif role == 'employee':
        page = st.sidebar.selectbox("Choose a page:", ["Home", "Question Bank", "Feedback Form"])
        if page == "Home":
            st.title(f"Welcome {user[1]}")
            st.write(f"{user[4]}")

            question_counts = get_question_counts()  
            difficulty_df = question_counts["difficulty_levels"]

            st.subheader("Question set")

# Stacked Bar Chart for Questions by Subject with Difficulty Levels as Stacks
            fig_difficulty = px.bar(
                difficulty_df,
                y="Subject",
                x="Count",
                color="Difficulty Level",
                orientation="h",  # Horizontal orientation
                title="Questions by Subject and Difficulty Level",
            )
            fig_difficulty.update_layout(barmode="stack", yaxis_title="Subject", xaxis_title="Count")
            st.plotly_chart(fig_difficulty, use_container_width=True)
            # 4. Questions by Difficulty Level: Separate Pie Chart
            st.write("Questions by Difficulty Level")
            fig_difficulty_levels = px.pie(difficulty_df, names="Difficulty Level", values="Count", title="Distribution of Question Difficulty Levels")
            fig_difficulty_levels.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_difficulty_levels, use_container_width=True)
            
    else:
        page = st.sidebar.selectbox("Choose a page:", ["Home", "Question Bank"])

    if page == "Home":
        
        if role == 'admin':
            st.write("Admin Content")
            admin_approval_section()
        elif role in ['trainer', 'employee']:
            st.write(f"{role.capitalize()} Content Here")

        if st.button("Edit Profile"):
            st.session_state.edit_mode = True

        if 'edit_mode' in st.session_state and st.session_state.edit_mode:
            edit_user_profile(user)

    elif page == "Create Questions" and (role == 'admin' or role == 'trainer'):
            question_generator_app()

    elif page == "Question Bank":
        display_questions_ui()
    elif page == "Edit Question Bank":
        edit_questions_table()
    
    elif page == "Feedback Summary" and role == 'admin':
        display_general_feedback()
    
    elif page == "Feedback Form" and role in ['employee', 'trainer']:
        feedback_form()



def edit_user_profile(user):
    """Allow users to edit their phone number and password."""
    st.subheader("Edit Profile")
    new_phone = st.text_input("Phone Number", value=user[5])
    new_password = st.text_input("Password", type="password")

    if st.button("Save Changes"):
        if new_phone and new_password:
            update_user_profile(user[0], new_phone, new_password)
            st.session_state.edit_mode = False
        else:
            st.error("Phone number and password cannot be blank.")

    if st.button("Back"):
        st.session_state.edit_mode = False
        st.experimental_set_query_params(dummy="1") 

def update_user_profile(user_id, new_phone, new_password):
    """Update phone number and password in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(new_password)

    try:
        cursor.execute("UPDATE users SET phone_number = ?, password = ?, status = 'approved' WHERE user_id = ?",
                       (new_phone, hashed_password, user_id))
        conn.commit()
        st.success("Profile updated successfully!")
    except Exception as e:
        st.error(f"Error updating profile: {e}")
    finally:
        conn.close()



def approve_user(email):
    """Approve a user by updating their status in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE users SET status = 'approved' WHERE email = ?", (email,))
        conn.commit()

        if cursor.rowcount > 0:
            st.session_state.approved_users.append(email)  # Track approved users
            st.success(f"User {email} approved successfully.")
        else:
            st.warning(f"No user found with email: {email}.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def admin_approval_section():
    """Section for admin to approve pending users."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, name, email, role FROM users WHERE status = 'pending'")
    pending_users = cursor.fetchall()

    st.subheader("Pending User Approvals")

    if pending_users:
        for user in pending_users:
            user_id, name, email, role = user
            st.write(f"Name: {name}, Email: {email}, Role: {role}")
            st.button(f"Approve {name}", key=f"approve_{user_id}", on_click=approve_user, args=(email,))
    else:
        st.write("No pending approvals.")

    conn.close()


def logout():
    """Clear session state for logout."""
    if 'user' in st.session_state:
        del st.session_state["user"]  # Clear user from session state
        
    
    return

if __name__ == "__main__":
    if 'user' not in st.session_state:
        st.warning("You need to log in first.")
    else:
        user = st.session_state.user
        display_dashboard(user)


def edit_user_profile(user):
    """Allow users to edit their phone number and password."""
    
    # Add custom CSS styles for buttons
    st.markdown("""
        <style>
            .edit-profile-container {
                background-color: #2a2a2a;  /* Dark background for the container */
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
                color: #f5f5f5;  /* Light text color */
                height:100px;
            }
            .edit-profile-title {
                color: #4b8be1;  /* Title color */
                font-size: 1.5em;
                margin-bottom: 10px;
                text-align: center;
            }
            .stTextInput {
                margin-top: 10px;
                width: 100%;
                max-width: 400px;
                align:center;
                margin-left:150px;  /* Set a max width for inputs */
            }
            /* Style for the Save button */
            .save-button {
                background-color: #4b8be1;  /* Button background color */
                color: white;  /* Button text color */
                border: none;  /* Remove button border */
                border-radius: 5px;  /* Rounded corners */
                padding: 10px;  /* Add padding */
                cursor: pointer;  /* Change cursor on hover */
            }
            .save-button:hover {
                background-color: #007bff;  /* Button hover color */
            }
            /* Style for the Edit button */
            .edit-button {
                background-color: #28a745;  /* Green background for Edit button */
                color: white;  /* Button text color */
                border: none;  /* Remove button border */
                border-radius: 5px;  /* Rounded corners */
                padding: 10px;  /* Add padding */
                cursor: pointer;  /* Change cursor on hover */
            }
            .edit-button:hover {
                background-color: #218838;  /* Darker green on hover */
            }
            .stError {
                color: #dd1c1c;  /* Error message color */
                font-weight: bold;  /* Bold error messages */
            }
        </style>
    """, unsafe_allow_html=True)

    # Profile edit form
    with st.container():
       
        st.markdown('<div class="edit-profile-title">Edit Profile</div>', unsafe_allow_html=True)
        
        # Create a form for editing profile
        with st.form(key='edit_profile_form'):
            new_phone = st.text_input("Phone Number", value=user[5])
            new_password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Save Changes")  # Removed key parameter

            if submit_button:
                if new_phone and new_password:
                    update_user_profile(user[0], new_phone, new_password)  # Assuming user[0] is user ID
                    st.session_state.edit_mode = False
                    st.success("Profile updated successfully!")
                else:
                    st.error("Phone number and password cannot be blank.")
        
        # Create an Edit button outside the form
        if st.button("Back"):
            st.session_state.edit_mode = False
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)  # Close the container

def update_user_profle(user_id, new_phone, new_password):
    """Update phone number and password in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(new_password)

    try:
        cursor.execute("UPDATE users SET phone_number = ?, password = ?, status = 'approved' WHERE user_id = ?",
                       (new_phone, hashed_password, user_id))
        conn.commit()
        st.success("Profile updated successfully!")
    except Exception as e:
        st.error(f"Error updating profile: {e}")
    finally:
        conn.close()

def admin_approval_section():
    """Section for admin to approve pending users."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, name, email, role FROM users WHERE status = 'pending'")
    pending_users = cursor.fetchall()

    st.subheader("Pending User Approvals")

    if pending_users:
        for user in pending_users:
            user_id, name, email, role = user
            st.write(f"Name: {name}, Email: {email}, Role: {role}")
            st.button(f"Approve {name}", key=f"approve_{user_id}", on_click=approve_user, args=(email,))
    else:
        st.write("No pending approvals.")

    conn.close()

  

if __name__ == "__main__":
    if 'user' not in st.session_state:
        st.warning("You need to log in first.")
        # Optionally, you can redirect to the login page
    else:
        user = st.session_state.user
        display_dashboard(user)