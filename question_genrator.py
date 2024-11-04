import streamlit as st
from google.generativeai import configure, GenerativeModel
from database_setup import setup_database, insert_question
import time  # Import time for simulating delays

def question_generator_app():
    # Set up your API key
    api_key = "AIzaSyAPJK8mjGNw08IwLvoyxY2NrLO1HbFISK0"  # Replace with your actual API key
    configure(api_key=api_key)

    # Initialize the database
    setup_database()

    # Initialize session state if not already done
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "description" not in st.session_state:
        st.session_state.description = ""
    if "num_questions" not in st.session_state:
        st.session_state.num_questions = 1
    if "question_type_index" not in st.session_state:
        st.session_state.question_type_index = 0  # Default to first option
    if "difficulty_index" not in st.session_state:
        st.session_state.difficulty_index = 0  # Default to first option
    if "subject" not in st.session_state:
        st.session_state.subject = ""

    st.title("Automated Question Builder Application")

    # Custom CSS styles for the application
    st.markdown("""
        <style>
            body {
                background-color: #f4f4f9; /* Light background color */
                font-family: 'Arial', sans-serif; /* Font style */
            }
            .main {
                max-width: 800px; /* Limit the width of the main content */
                margin: auto; /* Center align */
                padding: 20px; /* Padding around the content */
                background-color: white; /* White background for the container */
                border-radius: 10px; /* Rounded corners */
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); /* Subtle shadow */
            }
            h1 {
                color: #333; /* Darker title color */
                text-align: center; /* Center align the title */
            }
            .stButton {
                color: white; /* White text color */
                
                border: none; /* Remove border */
                border-radius: 5px; /* Rounded corners */
                padding: 10px 20px; /* Padding inside buttons */
                cursor: pointer; /* Pointer cursor on hover */
                font-size: 16px; /* Font size */
                transition: background-color 0.3s, transform 0.2s; /* Smooth transition */
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* Subtle shadow */
            }
            .stButton:hover {
                background-color: #0056b3; /* Darker blue on hover */
                transform: scale(1.05); /* Slight scale effect */
            }
            .stButton:active {
                background-color: #004085; /* Even darker blue on click */
                box-shadow: inset 0 4px 10px rgba(0, 0, 0, 0.2); /* Inner shadow for active state */
            }
            .stTextInput, .stTextArea, .stSelectbox, .stNumberInput {
                border-radius: 5px; /* Rounded corners */
                border: 1px solid #ccc; /* Light border */
                padding: 10px; /* Padding inside inputs */
                width: 100%; /* Full width */
                transition: border-color 0.3s; /* Smooth transition */
            }
            .stTextInput:focus, .stTextArea:focus, .stSelectbox:focus, .stNumberInput:focus {
                border-color: #4CAF50; /* Change border color on focus */
                outline: none; /* Remove outline */
            }
            .success {
                color: green;
            }
            .error {
                color: red;
            }
        </style>
    """, unsafe_allow_html=True)

    # Main content container
    with st.container():
        
        # Get the current state
        description = st.text_area("Enter the question description:", value=st.session_state.description)
        num_questions = st.number_input("Number of questions to generate:", min_value=1, max_value=100, value=st.session_state.num_questions)

        # Adding options for question type, difficulty level, and subject
        question_types = ["Multiple Choice", "Coding", "Short Answer", "Case Study"]
        difficulty_levels = ["Easy", "Medium", "Hard"]

        question_type = st.selectbox("Select question type:", question_types, index=st.session_state.question_type_index)
        difficulty_level = st.selectbox("Select difficulty level:", difficulty_levels, index=st.session_state.difficulty_index)
        subject = st.text_input("Enter the subject:", value=st.session_state.subject)

        # Update session state with current inputs
        st.session_state.description = description
        st.session_state.num_questions = num_questions
        st.session_state.question_type_index = question_types.index(question_type)
        st.session_state.difficulty_index = difficulty_levels.index(difficulty_level)
        st.session_state.subject = subject

        # Function to generate questions
        def generate_questions(description, num_questions, question_type, difficulty_level):
            questions = []
            for _ in range(num_questions):
                if question_type == "Multiple Choice":
                    prompt = (f"Generate a unique multiple-choice question at a {difficulty_level} level based on the following description: {description}. "
                              "Provide the question and four options, without answers or explanations.")
                else:
                    prompt = (f"Generate a unique {question_type} question at a {difficulty_level} level based on the following description: {description}. "
                              "Provide only the question, without answers or explanations.")
                
                model = GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                questions.append((response.text.strip(), ["Option A", "Option B", "Option C", "Option D"]))  # Dummy options for non-MCQ types
            
            return questions

        if st.button("Generate Questions"):
            if description:
                with st.spinner("Generating questions..."):  # Show spinner
                    time.sleep(2)  # Simulate processing time (optional)
                    st.session_state.questions = generate_questions(description, num_questions, question_type, difficulty_level)
                st.success("Questions generated successfully!")
                st.subheader("Generated Questions:")
                for idx, (question, options) in enumerate(st.session_state.questions, start=1):
                    st.write(f"{idx}. {question}")
                    if question_type == "Multiple Choice":
                        st.write("**Options**: " + ", ".join(options))
            else:
                st.error("Please enter a description to generate questions.")

        if st.button("Save Questions"):
            if st.session_state.questions:
                for question, options in st.session_state.questions:
                    insert_question(question, description, question_type, difficulty_level, subject)
                    st.success(f"Question '{question}' saved to the database successfully!")
                st.session_state.questions = []  # Clear questions after saving
            else:
                st.error("No questions generated to save. Please generate questions first.")
            if st.button("Back"):
                st.session_state.edit_mode = False
                st.rerun()

