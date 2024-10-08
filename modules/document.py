import streamlit as st
from streamlit_option_menu import option_menu
import firebase_admin
from firebase_admin import credentials,auth
from dotenv import load_dotenv, dotenv_values
import os
import re
import time
import PyPDF2
import pinecone
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

def document():
    # st.title(f'Welcome to :red[PdfBot] {st.session_state['user_name']}')
    st.title('Welcome to PdfBot ' + st.session_state['user_name'])
    build_doc_ui()

def upload_doc() -> None:
    docs = st.file_uploader("Upload documents", accept_multiple_files=True)
    if st.button("Upload") and docs is not None:
        try:
            with st.status("Uploading data...", expanded=True) as status:
                for doc in docs:
                    st.write("Fetching data...")
                    file,file_name = uploadtoPineCone(doc)
                    if file is not None:
                        st.write("Splitting data...")
                    chunks = splitData(file)
                    if chunks is not None:
                        st.write("Embedding data...")
                    embeddings = convertUploadedFileToEmbeddings(chunks)
                    if embeddings is not None:
                        st.write("storing data...")
                    store = storeToVectorDB(chunks, embeddings, file_name)
                    if store == "Success":
                        status.update(label="Upload complete!", state="complete", expanded=False)
        except:
            st.error("Please select valid document")

def uploadtoPineCone(documents):
    for doc in documents:
        sanitized_filename = sanitizeFileName(documents.name)
        file = readFile(documents)
        return file,sanitized_filename

def sanitizeFileName(file_name):
    filename_lower = file_name.lower()
    sanitized_filename = re.sub(r'[^a-z0-9\.]', '', filename_lower)
    return sanitized_filename

def readFile(path):
    """Converts the PDF from Path to a single String - delimited by \n"""
    # Read the file
    readData = PyPDF2.PdfReader(path)

    # Initiate the text 
    text = ""

    for page in readData.pages:
        if page:
            text += (page.extract_text() + "\n")

    print(f"Length of text : {len(text)}")
    return text

def splitData(data):
    """Splits the data into chunks of 1000 words each"""

    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap  = 50,
    length_function = len,
    add_start_index = True,
)
    texts = text_splitter.create_documents([data])
    texts = [ text.page_content for text in texts]
    print(f"Length of texts : {len(texts)}")
    return texts

def convertUploadedFileToEmbeddings(file):
    max_retries = 3
    retry_delay = 60  # in seconds

    for attempt in range(max_retries):
        try:
            embeddingModel = OpenAIEmbeddings(openai_api_key=st.session_state['OPEN_AI_KEY'])
            
            # Ensure file is in correct format
            if isinstance(file, str):
                documents = [line.strip() for line in file.splitlines()]
            elif isinstance(file, list):
                documents = file
            else:
                raise TypeError("File must be a string or list of strings.")
            
            embeddings = embeddingModel.embed_documents(documents)
            print(f"Generated {len(embeddings)} embeddings.")
            return embeddings
        
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if "insufficient_quota" in str(e):
                # Wait before retrying if quota is insufficient
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return []
            else:
                return []

    return []

def storeToVectorDB(data, embeddings, file_name):
    pc = Pinecone(api_key=st.session_state['PINECONE_API_KEY'])
    index = pc.Index("pdfbot")
    if 'pdfbot' not in pc.list_indexes().names():
        pc.create_index(
            name='pdfbot', 
            dimension=1536, 
            metric='euclidean',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-west-2'
            )
        )
    else:
        f_name = file_name + '-' + st.session_state['user_name']
        datadict = converListToDict(data, embeddings)
        index.upsert(datadict, namespace=f_name)
        return "Success"

def converListToDict(data, embeddings):
    dictData = []
    numData = len(data)
    for i in range(numData):
        dictData.append({"id": str(i), "values": embeddings[i], "metadata":{"values": data[i],"user_id":st.session_state['user_name']}})

    return dictData

def pinecone_instance(data):
    pc = Pinecone(api_key=st.session_state['PINECONE_API_KEY'])
    index = pc.Index("pdfbot")
    return pc,index

def getDocList():
    pc = Pinecone(api_key=st.session_state['PINECONE_API_KEY'])
    index = pc.Index("pdfbot")
    doc_names = index.describe_index_stats()
    for name in doc_names["namespaces"].keys():
        get_name = name.split('-')
        if get_name[1] == st.session_state['user_name']:
            st.session_state['doc_names'].append(name.split('-')[0])

def showDocs():
    pc = Pinecone(api_key=st.session_state['PINECONE_API_KEY'])
    index = pc.Index("pdfbot")
    st.subheader("Your Uploaded Documents")
    i=1
    for name in st.session_state['doc_names']:
        st.write(f"{i}."+" "+f"{name}")
        i+=1
    st.divider()
    st.subheader("Select Document to delete from the :red[PdfBot]")
    try:
        options = st.selectbox("Select Document to Delete from :red[PdfBot]",options=st.session_state['doc_names'])
        if options is not None:
            if st.button("Delete"):    
                name = name+"-"+st.session_state['user_name']
                print('name------>')
                index.delete(namespace=name, delete_all=True)
                st.success("Delete Your Document Successfully")
                st.rerun()
            return True
    except Exception as e:
        return e

def doc_navbar() -> None:
    """
    Creates the side navigaton bar
    """
    main_navbar = st.empty()
    with main_navbar:
        selected = option_menu(
            menu_title=None,
            default_index=0,
            options=['Documents','Upload Document'],
            icons=['file-earmark-pdf','file-earmark-arrow-up',],
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "red", "font-size": "18px"}, 
                "nav-link": {"font-size": "18px", "text-align": "left", "margin":"0px","--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "black"},
                "nav-item":{"margin-left":"10px","margin-right":"10px"}
            }
        )
        return selected

def build_doc_ui():
    if st.session_state['log_in'] == False:
        st.error("Please Login/SignUp to check and Upload Documents")
    else:
        selected = doc_navbar()

        if selected == "Upload Document":
            upload_doc()
        if selected == "Documents":
            getDocList()
            showDocs()