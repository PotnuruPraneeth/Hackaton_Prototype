import streamlit as st
import google.generativeai as genai
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Test Case Generator",
    page_icon="🧪",
    layout="wide"
)

# --- App Header ---
st.title("🧪 AI-Powered Test Case Generator")
st.caption("For Healthcare Software Requirements | Built with Google Gemini")


# --- API Key Configuration ---
try:
    # Configure the Gemini API key from Streamlit secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    st.sidebar.success("API key configured successfully!")
except Exception as e:
    st.sidebar.error("API key not found. Please add it to your Streamlit secrets.")
    st.stop()


# --- The Master Prompt ---
master_prompt_template = """
You are an expert Quality Assurance (QA) Engineer with deep specialization in regulated healthcare software. Your expertise includes compliance with standards like HIPAA, FDA, and ISO 13485.

Your task is to analyze the following software requirement and generate a comprehensive set of professional test cases.

For each generated test case, you MUST strictly adhere to the following structure. Use Markdown for formatting.

---

**Test Case ID:** `TC-[Requirement_ID]-##` (e.g., TC-REQ-101-01)
**Title:** A clear, concise title summarizing the test objective.
**Description:** A brief 1-2 sentence explanation of what this test case is validating.
**Priority:** [High, Medium, or Low]
**Test Type:** [Functional, Negative, Edge Case, Security, UI/UX]

**Preconditions:**
- A numbered list of all conditions that must be true before starting the test. (e.g., 1. User is logged in as a 'Doctor'. 2. Patient 'John Doe' exists in the system.)

**Test Steps:**
- A numbered list of clear, simple, and unambiguous actions for a manual tester to perform.

**Expected Results:**
- A clear and specific description of the expected outcome after the final test step is performed. It should be a single, verifiable result.

---

**IMPORTANT INSTRUCTIONS:**
1.  Generate a "Functional" test case that validates the primary success scenario (the "happy path").
2.  You MUST also generate at least one "Negative" test case (e.g., testing invalid data input, incorrect permissions).
3.  If applicable, generate an "Edge Case" test case (e.g., testing boundary limits, zero values, special characters).
4.  show it in jason format also for jira integration.

Here is the requirement to be tested:

**Requirement ID:** {req_id}
**Requirement Text:** {req_text}
"""


# --- Function to call the Gemini API ---
def generate_test_cases(req_id: str, req_text: str, output_container):
    """
    Generates test cases and streams the output directly to a container.
    """
    if not req_id or not req_text:
        output_container.error("Error: Requirement ID and Text cannot be empty.")
        return

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        final_prompt = master_prompt_template.format(req_id=req_id, req_text=req_text)
        response = model.generate_content(final_prompt, stream=True)

        # Use an empty placeholder in the container to append the text
        live_text = output_container.empty()
        full_response = ""
        for chunk in response:
            if chunk.text:
                full_response += chunk.text
                live_text.markdown(full_response) # Update the placeholder with the new text

    except Exception as e:
        output_container.error(f"An error occurred: {str(e)}")


# --- Streamlit User Interface ---

# Use columns for a cleaner layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Enter Software Requirement")
    # Input fields for the user
    req_id_input = st.text_input("Requirement ID", placeholder="e.g., REQ-045")
    req_text_input = st.text_area("Requirement Text", height=200, placeholder="As a doctor, I want to search for a patient by last name...")

    # Generate button
    if st.button("✨ Generate Test Cases", type="primary", use_container_width=True):
        with col2:
            st.subheader("Generated Test Cases")
            # Create a container to hold the streaming output
            output_area = st.container() 
            with st.spinner("🤖 AI is thinking... Please wait."):
                 # **THE FIX IS HERE:** Pass the 'output_area' to the function
                 generate_test_cases(req_id_input, req_text_input, output_area)


with st.sidebar:
    st.header("About")
    st.info("This prototype uses Google's Gemini model to automatically generate test cases from software requirements, demonstrating a significant reduction in manual effort for QA teams in regulated industries.")
    st.header("Sample Requirements")
    st.markdown("""
    **Simple:**
    `As a doctor, I want to be able to search for a patient by their last name so that I can quickly find their record.`

    **Complex:**
    `The system must log all access to patient records in an immutable, HIPAA-compliant audit trail.`
    """)
