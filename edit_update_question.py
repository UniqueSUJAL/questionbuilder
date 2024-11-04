import streamlit as st
from database_setup import get_unique_subjects, get_filtered_questions, delete_question, update_question

def edit_questions_table():
    st.title("Filter Questions")

    # Load subjects from the database
    subjects = get_unique_subjects()
    filter_subject = st.selectbox("Filter by subject:", ["All"] + subjects)
    filter_question_type = st.selectbox("Filter by question type:", ["All", "Multiple Choice", "Coding", "Short Answer", "Case Study"])
    filter_difficulty_level = st.selectbox("Filter by difficulty level:", ["All", "Easy", "Medium", "Hard"])

    # Button to apply filters
    if st.button("Apply Filters"):
        st.session_state["refresh_needed"] = True  # Set refresh_needed flag

    # Refresh questions list if needed
    if st.session_state.get("refresh_needed", True):
        filtered_questions = get_filtered_questions(
            subject=filter_subject if filter_subject != "All" else None,
            question_type=filter_question_type if filter_question_type != "All" else None,
            difficulty_level=filter_difficulty_level if filter_difficulty_level != "All" else None
        )
        st.session_state["filtered_questions"] = filtered_questions  # Store questions in session state
        st.session_state["refresh_needed"] = False  # Reset refresh flag

    # Display questions
    if st.session_state.get("filtered_questions"):
        for i, question in enumerate(st.session_state["filtered_questions"], start=1):
            question_id, question_text, description, question_type, difficulty_level, subject = question

            # Initialize edit mode for each question
            if f"edit_mode_{question_id}" not in st.session_state:
                st.session_state[f"edit_mode_{question_id}"] = False

            # Display question details
            if not st.session_state[f"edit_mode_{question_id}"]:
                st.write(f"**Question {i}**")
                st.write(question_text)
                st.write(f"Type: {question_type} | Difficulty: {difficulty_level} | Subject: {subject}")

                # Edit and Delete buttons
                if st.button(f"Edit {question_id}", key=f"edit_{question_id}"):
                    st.session_state[f"edit_mode_{question_id}"] = True

                if st.button(f"Delete {question_id}", key=f"delete_{question_id}"):
                    delete_question(question_id)  # Delete question from database
                    st.success("Question deleted successfully!")
                    st.session_state["refresh_needed"] = True  # Refresh questions

            # Edit question form
            else:
                with st.form(key=f"edit_form_{question_id}"):
                    new_question = st.text_input("Question:", value=question_text)
                    new_description = st.text_area("Description:", value=description)
                    new_question_type = st.selectbox("Question Type:", ["Multiple Choice", "Coding", "Short Answer", "Case Study"], index=["Multiple Choice", "Coding", "Short Answer", "Case Study"].index(question_type))
                    new_difficulty_level = st.selectbox("Difficulty Level:", ["Easy", "Medium", "Hard"], index=["Easy", "Medium", "Hard"].index(difficulty_level))
                    new_subject = st.selectbox("Subject:", ["All"] + subjects, index=subjects.index(subject))

                    submit_button = st.form_submit_button("Update Question")
                    if submit_button:
                        update_question(question_id, new_question, new_subject, new_question_type, new_difficulty_level)
                        st.session_state[f"edit_mode_{question_id}"] = False
                        st.success("Question updated successfully!")
                        st.session_state["refresh_needed"] = True  # Refresh questions

if __name__ == "__main__":
    edit_questions_table()
