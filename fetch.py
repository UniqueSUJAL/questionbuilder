import streamlit as st
import pandas as pd
from fpdf import FPDF  # For generating PDF files
import spacy  # Import spaCy
import re
from database_setup import get_unique_subjects, get_filtered_questions
import subprocess
# Load the spaCy model
if not os.path.exists('en_core_web_sm'):
    
    subprocess.call(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
nlp = spacy.load("en_core_web_sm")

# Extract question and options using spaCy
def extract_question_and_options(question_text):
    cleaned_question = question_text.replace('**', '').strip()
    prefixes = ["## Question:", "Question:"]

    for prefix in prefixes:
        if cleaned_question.lower().startswith(prefix.lower()):
            cleaned_question = cleaned_question[len(prefix):].strip()

    parts = cleaned_question.split('Options:', 1)

    if len(parts) > 1:
        question_part = parts[0].strip()
        options_text = parts[1].strip()
        options_lines = re.split(r'\s*(?=[A-Da-d][.)]\s)', options_text)
        options_text = "\n".join(line.strip() for line in options_lines if line.strip())
    else:
        lines = cleaned_question.splitlines()
        question_part = lines[0].strip()
        options_text = "No options available" if len(lines) == 1 else "\n".join(line.strip() for line in lines[1:])

    return question_part, options_text

# Generate PDF with the filtered data
def generate_pdf(data, subject, difficulty):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add subject and difficulty level at the top
    # To be used in other files
    pdf.cell(200, 10, txt="Questions Report", ln=True, align='C')
    pdf.ln(10)  # Add space between title and content
    pdf.cell(0, 10, txt=f"Subject: {subject}", ln=True)
    pdf.cell(0, 10, txt=f"Difficulty Level: {difficulty}", ln=True)
    pdf.ln(5)  

    for idx, (sno, question, options) in enumerate(data, start=1):
        pdf.multi_cell(0, 10, f"{sno}. {question}")
        pdf.ln(5)
        pdf.multi_cell(0, 10, "Options:\n" + options.replace('<br>', '\n'))  # Ensure options are formatted correctly
        pdf.ln(10)

    pdf_file_path = "filtered_questions.pdf"
    pdf.output(pdf_file_path)
    return pdf_file_path

# Display the Questions Table with filters and download options
def display_questions_table():
    st.markdown(""" 
        <style>
        .title { text-align: center; font-size: 36px; font-weight: bold; margin-bottom: 20px; color: #333; }
        .dataframe { border-collapse: collapse; width: 100%; margin: auto; }
        .dataframe thead th { font-size: 22px; font-weight: bold; background-color: #4CAF50; color: white; padding: 12px; text-align: center; }
        .dataframe tbody td { font-size: 18px; padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        .dataframe tbody td.Question { font-size: 25px; font-weight: bold; width: 50%; }
        .dataframe tbody td.Options { font-size: 18px; color: #555; width: 90%; }
        .dataframe-title { font-size: 34px; font-weight: bold; text-align: center; margin: 20px 0; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="title">Filter Questions</div>', unsafe_allow_html=True)

    subjects = get_unique_subjects()
    filter_subject = st.selectbox("Filter by subject:", ["All"] + subjects)
    filter_question_type = st.selectbox(
        "Filter by question type:", ["All", "Multiple Choice", "Coding", "Short Answer", "Case Study"]
    )
    filter_difficulty_level = st.selectbox(
        "Filter by difficulty level:", ["All", "Easy", "Medium", "Hard"]
    )

    if st.button("Apply Filters"):
        filtered_questions = get_filtered_questions(
            subject=filter_subject if filter_subject != "All" else None,
            question_type=filter_question_type if filter_question_type != "All" else None,
            difficulty_level=filter_difficulty_level if filter_difficulty_level != "All" else None
        )

        if filtered_questions:
            table_data = []
            for i, q in enumerate(filtered_questions, start=1):
                q_id, q_text, q_type, q_difficulty, q_subject = q[:5]
                question_display, options_display = extract_question_and_options(q_text)
                options_display = options_display.replace('\n', '<br>')  # Replace newlines with <br> for HTML display
                table_data.append([i, question_display, options_display])
                
            df = pd.DataFrame(table_data, columns=["S.No", "Question", "Options"])
            st.markdown('<div class="dataframe-title">Questions Table</div>', unsafe_allow_html=True)

            # Convert DataFrame to HTML
            html_table = df.to_html(index=False, escape=False, classes="dataframe")
            st.write(html_table, unsafe_allow_html=True)

            # Download as CSV
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download as CSV", data=csv_data, file_name="filtered_questions.csv", mime="text/csv")

            # Download as PDF
            pdf_file = generate_pdf(table_data, filter_subject, filter_difficulty_level)
            with open(pdf_file, "rb") as f:
                st.download_button("Download as PDF", data=f, file_name=pdf_file, mime="application/pdf")
        else:
            st.write("No questions found for the selected filters.")

# Function to display the Question Bank UI
def display_questions_ui():
    st.title("Question Bank")
    display_questions_table()

# To be used in other files
def question_bank_ui():
    display_questions_ui()

if __name__ == "__main__":
    question_bank_ui()
