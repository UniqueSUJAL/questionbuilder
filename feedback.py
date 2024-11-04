import streamlit as st
import re
from database_setup import (
    fetch_questions,
    submit_feedback,
    get_unique_subjects,
    get_filtered_questions,
    get_feedback_summary,
    get_general_feedback_summary,
    update_feedback_status,
    get_subjects
)
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Email sending function
def send_thank_you_email(user_email, feedback_details):
    """Send a thank-you email to the user for their feedback."""
    sender_email = "questionsgenratorind@gmail.com"  # Replace with your sender email
    sender_password = "gvwyekaphpkfqmos"  # Replace with your email password

    subject = "Thank You for Your Feedback!"
    body = f"""\
    Dear Valued User,

    We sincerely appreciate you taking the time to provide your feedback. Your insights are incredibly valuable in helping us improve our services and better meet your needs.
    Here are the details of your feedback for your reference:
    {feedback_details}

    Thank you once again for your contribution. Should you have any further suggestions or require assistance, please feel free to reach out.

    Warm regards,

    The Questions Generator Team
    questionsgenratorind@gmail.com
    © 2024 Questions Generator Inc. All rights reserved.
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Correct SMTP server for Gmail
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, user_email, msg.as_string())
        st.success(f"Thank-you email sent to {user_email}.")
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")


# Text cleaning function
def clean_text(text):
    """Remove unwanted characters from text using regex."""
    cleaned_text = re.sub(r"[#*\"']", "", text)
    return cleaned_text.strip()

def feedback_form():
    """Render the feedback form in Streamlit."""
    st.title("Feedback Form")

    # CSS for styling
    st.markdown("""
        <style>
            body {
                background-color: #000; /* Black background */
                color: #fff; /* White text */
                font-size: 18px; /* Increased text size */
            }
            .submit-button {
                background-color: #444; /* Darker button color */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                cursor: pointer;
                font-size: 16px;
            }
            .submit-button:hover {
                background-color: #666; /* Lighter button color on hover */
            }
            h1, h2, h3 {
                 /* White headings */
                font-size: 24px; /* Increased heading size */
            }
            .stSelectbox, .stTextInput, .stTextArea, .stSlider {
                /* Dark input fields */
                color: white; /* White text in input fields */
                border: 1px solid #444; /* Dark border */
                border-radius: 5px;
                font-size: 20px; 
                align:center;/* Increased input field text size */
            }
            .stSelectbox:focus, .stTextInput:focus, .stTextArea:focus, .stSlider:focus {
                border-color: #ffffff; /* Lighter border on focus */
            }
        </style>
    """, unsafe_allow_html=True)

    # Check if the user is logged in
    if 'user' not in st.session_state or st.session_state.user is None:
        # Redirect to the login page
        st.session_state["login_redirect"] = True  # Set a flag for redirection
        return  # Early exit if the user is not logged in

    user_id = st.session_state.user[0]  # Assuming user ID is the first element in the user tuple

    feedback_type = st.selectbox("Feedback Type", ["General Feedback"])

    # if feedback_type == "Question Feedback":
    #     subjects = get_unique_subjects()  # Fetch unique subjects from the database
    #     subject = st.selectbox("Subject", subjects)

    #     questions = get_filtered_questions(subject=subject)  # Get questions based on selected subject

    #     if questions:
    #         # Clean each question and format it
    #         question_options = [f"{q[0]}: {clean_text(q[1])}" for q in questions]  # Format as "ID: Cleaned Question"
    #         selected_question = st.selectbox("Select Question", question_options)

    #         # Extract the question ID from the selected option
    #         question_id = int(selected_question.split(":")[0]) if selected_question else None

    #         # Rating scale explanation
    #         st.markdown(""" 
    #         **Rating Scale:**
    #         - **1:** Poor
    #         - **2:** Fair
    #         - **3:** Good
    #         - **4:** Very Good
    #         - **5:** Excellent
    #         """)

    #         # Collect feedback details
    #         rating = st.slider("Rating", 1, 5)
    #         comment = st.text_area("Comment")

    #         if st.button("Submit Feedback"):
    #             if question_id is not None and comment.strip():  # Ensure question is selected and comment is not empty
    #                 cleaned_comment = clean_text(comment)
    #                 submit_feedback(user_id, question_id, rating, cleaned_comment)
    #                 st.success("Feedback submitted successfully!")

    #     # Extract email and validate it
    #                 user_email = st.session_state.user[2].strip()  # Ensure this is the correct index
    #                 if "@" in user_email and "." in user_email.split("@")[-1]:
    #                     send_thank_you_email(user_email, cleaned_comment)
    #                 else:
    #                     st.error("Invalid email address in user data.")
    #                     print(f"Error: Invalid email {user_email}")
    #             elif not comment.strip():
    #                     st.error("Comment box cannot be empty.")
    #             else:
    #                 st.error("Please select a question.")

        # else:
        #     st.warning("No questions available for the selected subject.")

    if feedback_type == "General Feedback":
        subject = st.text_input("Subject/Topic")

        # Rating scale explanation
        st.markdown(""" 
        **Rating Scale:**
        - **1:** Poor
        - **2:** Fair
        - **3:** Good
        - **4:** Very Good
        - **5:** Excellent
        """)

        rating = st.slider("Rating", 1, 5)
        comment = st.text_area("Comment")

        if st.button("Submit Feedback"):
            if comment.strip():  # Ensure comment is not empty
                cleaned_comment = clean_text(comment)
                submit_feedback(user_id, None, rating, cleaned_comment)
                st.success("Feedback submitted successfully!")
                send_thank_you_email(st.session_state.user[2], cleaned_comment)  # Assuming email is the second element in the user tuple
            else:
                st.error("Comment box cannot be empty.")


# def feedback_summary():
#     """Display feedback summary for a specific subject."""
#     st.title("Feedback Summary")

#     # Add custom CSS styling
#     st.markdown("""
#         <style>
#             body {
#                 font-family: Arial, sans-serif;
#                 margin: 20px;
#             }
#             h1, h2 {
#                 color: #333;
#             }
#             .feedback-title {
#                 font-size: 1.5em;
#                 color: #333;
#                 margin-bottom: 10px;
#             }
#             .feedback-item {
#                 margin: 10px 0;
#                 padding: 10px;
#                 border: 1px solid #ccc;
#                 border-radius: 5px;
#                 background-color: #f9f9f9;
#                 box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
#             }
#             .feedback-item h4 {
#                 margin: 0;
#             }
#             .mark-seen-button {
#                 background-color: #007BFF; /* Bootstrap Primary Color */
#                 color: white;
#                 border: none;
#                 padding: 8px 12px;
#                 text-align: center;
#                 text-decoration: none;
#                 display: inline-block;
#                 font-size: 14px;
#                 border-radius: 5px;
#                 cursor: pointer;
#                 margin-top: 5px;
#             }
#             .mark-seen-button:hover {
#                 background-color: #0056b3; /* Darker shade */
#             }
#             .error {
#                 color: red;
#                 font-weight: bold;
#             }
#         </style>
#     """, unsafe_allow_html=True)

#     # Dropdown for selecting a subject
#     # Streamlit code for feedback summary
    

#     # Button to fetch feedback
#     subjects = get_subjects()
#     subject = st.selectbox("Select Subject", subjects)

#     # Button to fetch feedback
#     if st.button("Fetch Feedback"):
#         # Fetch feedback details for the selected subject
#         feedback_details = get_feedback_summary(subject)

#         # Check if feedback details are valid
#         if feedback_details is None or not feedback_details:
#             st.warning("No feedback found for this subject.")
#             return  # Exit early if there's no feedback

#         st.session_state["feedback_details"] = feedback_details  # Store feedback in session state

#         # Inspect feedback details
#         st.write("Feedback Details:", feedback_details)  # Debug line

#         feedback_df = pd.DataFrame(feedback_details)

#         # Check for required columns
#         required_columns = {"email", "question_id", "subject", "type", "level", "question_text", "comment", "rating", "status"}
#         missing_columns = required_columns - set(feedback_df.columns)

#         if missing_columns:
#             st.error(f"Missing columns in feedback DataFrame: {', '.join(missing_columns)}")
#         else:
#             # Custom format for displaying feedback
#             for _, row in feedback_df.iterrows():
#                 st.markdown('<div class="feedback-item">', unsafe_allow_html=True)  # Start feedback item
#                 st.markdown(f"**Email:** {row['email']}")
#                 st.markdown(f"**Question ID:** {row['question_id']}  |  **Subject:** {row['subject']}  |  **Type:** {row['type']}  |  **Level:** {row['level']}")
#                 st.markdown(f"**Question:** {row['question_text']}")
#                 st.markdown(f"**Comment:** {row['comment']}  |  **Rating:** {row['rating']}")
#                 st.markdown(f"**Status:** {row['status']}")
#                 st.markdown('</div>', unsafe_allow_html=True)  # End feedback item

#                 # Session state tracking if feedback is "seen"
#                 feedback_id = row.get("feedback_id")  # Use get to avoid KeyError if key is missing
#                 if feedback_id is not None and f"seen_{feedback_id}" not in st.session_state:
#                     st.session_state[f"seen_{feedback_id}"] = row["status"] == "seen"

#                 # Button to mark feedback as seen
#                 if feedback_id is not None and not st.session_state[f"seen_{feedback_id}"]:
#                     if st.button(f"Mark as Seen ({feedback_id})", key=f"mark_seen_{feedback_id}", help="Click to mark this feedback as seen"):
#                         update_feedback_status(feedback_id, "seen")
#                         st.session_state[f"seen_{feedback_id}"] = True
#                         st.success(f"Feedback for Question ID {feedback_id} marked as seen.")
                        
#                         # Refresh the feedback details after marking as seen
#                         feedback_details = get_feedback_summary(subject)
#                         st.session_state["feedback_details"] = feedback_details
#     else:
#         st.write("Please select a subject and fetch feedback.")
# # Display general feedback function
def display_general_feedback():
    """Render the general feedback display in Streamlit."""
    st.title("General Feedback Summary")

    feedback_details = get_general_feedback_summary()

    if feedback_details:
        feedback_df = pd.DataFrame(feedback_details)

        if 'email' not in feedback_df.columns:
            st.error("The column 'email' does not exist in the feedback DataFrame.")
            return

        # Add a Serial Number column
        feedback_df.insert(0, 'S.No', range(1, len(feedback_df) + 1))

        st.subheader("All General Feedback")

        # Convert the DataFrame to HTML
        html_feedback_table = feedback_df.to_html(classes='feedback-table', index=False)

        # Add custom CSS styling for the table
        st.markdown("""
            <style>
                .feedback-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    background-color: black; /* Black background for the table */
                    color: white; /* White text color */
                }
                .feedback-table th, .feedback-table td {
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #ddd;
                }
                .feedback-table th {
                    background-color: #444; /* Darker shade for the header */
                    color: white; /* White text for header */
                }
                .feedback-table tr {
                    background-color: black; /* Black background for all rows */
                }
                /* Remove hover effect */
            </style>
        """, unsafe_allow_html=True)

        # Display the HTML table
        st.markdown(html_feedback_table, unsafe_allow_html=True)

        # Add functionality to mark feedback as seen
        for _, row in feedback_df.iterrows():
            feedback_id = row['id']
            user_email = row.get('email', "N/A")

            if f"seen_{feedback_id}" not in st.session_state:
                st.session_state[f"seen_{feedback_id}"] = row['status'] == 'seen'

            # Add a button to mark feedback as seen
            if not st.session_state[f"seen_{feedback_id}"]:
                if st.button(f"Mark as Seen ({feedback_id})", key=f"mark_seen_general_{feedback_id}"):
                    update_feedback_status(feedback_id, 'seen')
                    st.session_state[f"seen_{feedback_id}"] = True
                    st.success(f"Feedback {feedback_id} marked as seen.")

                    feedback_detail_str = f"Rating: {row['rating']}, Comment: {row['comment']}, Status: seen"
                    send_thank_you_email(user_email, feedback_detail_str)

    else:
        st.write("No general feedback available.")
