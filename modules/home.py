import streamlit as st
from modules import account,document

def home():
    st.title("Welcome to :red[PdfBot]")
    st.markdown("""
    Imagine having the power to effortlessly analyze complex documents, uncover insights, and receive instant 
    responses to your queries, all from one centralized location. **PdfBot** does exactly that by harnessing 
    the latest advancements in natural language processing and machine learning.

    ### Here's how you can get started:
    - **Upload your document:** Begin by uploading your document in PDF or DOCX format.
    - **Ask your questions:** Simply type your query in the chat interface.
    - **Get instant answers:** PdfBot will analyze your document and provide precise responses, tailored to your needs.

    **PdfBot** is not just a tool, but a sophisticated assistant, designed to streamline your workflow and 
    enhance your productivity. Whether you're working with legal contracts, academic papers, or corporate 
    reports, PdfBot empowers you with the ability to extract and understand information like never before.

    Get started now, and experience the future of document management with **PdfBot**.
    """)