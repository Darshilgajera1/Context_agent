import streamlit as st
from dotenv import load_dotenv

def credentials():
    st.title("Enter your Credentials")

    # Load environment variables
    load_dotenv()

    # Create a form to input credentials
    with st.form(key='credentials_form'):
        openai_key = st.text_input(
            "OpenAI API Key", 
            value=st.session_state.get('OPEN_AI_KEY', '')  # Pre-populate if already set
        )
        submit_button = st.form_submit_button(label="Save Credentials")

        if submit_button:
            if openai_key:
                st.session_state['OPEN_AI_KEY'] = openai_key
                st.success("Credentials saved successfully!")
                st.rerun()  # Force rerun to persist state
            else:
                st.error("Please provide your OpenAI Key.")
