import streamlit as st
from streamlit_option_menu import option_menu
from modules import account, home, chat, document, Crednetials
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

st.set_page_config(page_title="PdfBot", page_icon=":material/picture_as_pdf:")

if 'log_in' not in st.session_state:
    st.session_state['log_in'] = False
if 'log_out' not in st.session_state:
    st.session_state['log_out'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ''
if 'OPEN_AI_KEY' not in st.session_state:
    st.session_state['OPEN_AI_KEY'] = None
if 'doc_names' not in st.session_state:
    st.session_state['doc_names'] = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "select_doc" not in st.session_state:
    st.session_state["select_doc"] = None


if not firebase_admin._apps:
    cred = credentials.Certificate('modules/service_acnt.json')  
    firebase_admin.initialize_app(cred)

class PdfBot:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        load_dotenv()
        # st.session_state['OPEN_AI_KEY'] = os.getenv("OPEN_AI_KEY")
        st.session_state["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
        st.session_state['doc_names'] = []
        with st.sidebar:
            app = option_menu(
                menu_title='PdfBot',
                options=['Home', 'Chat', 'My Documents', 'My Account', 'Crednetials'],
                icons=['house-fill', 'chat-left-text-fill', 'files', 'person-circle'],
                menu_icon='filetype-pdf',
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "#262730"},  # Dark gray for dark mode
                    "menu-icon": {"color": "white", "font-size": "34px"},  # Adjust icon color to white
                    "menu-title": {"font-size": "34px", "text-align": "center", "font-weight": "bold", "color": "white"},  # White title
                    "icon": {"color": "white", "font-size": "22px"},  # White icons
                    "nav-link": {
                        "font-size": "18px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#333333",  # Dark hover color
                        "color": "white",  # Default link text color
                    },
                    "nav-link-selected": {"background-color": "#444444", "color": "white"},  # Darker gray for selected link
                    "title": {"font-size": "24px", "color": "white"}  # White text for title
                }

            )

        if app == "Home":
            home.home()
        elif app == "Chat":
            chat.start_chat()
        elif app == "My Documents":
            document.document()
        elif app == 'My Account':
            account.account()
        elif app == "Crednetials":
            Crednetials.credentials()


    run()
