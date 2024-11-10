import streamlit as st
import openai
import re
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
import chromadb.api
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
import warnings
import tempfile
import os
import base64
from pathlib import Path
from pydub.playback import play
import speech_recognition as sr
from pydub import AudioSegment
import time
from transcript_summarize import transcribe_audio, summarize_text
from langchain.text_splitter import RecursiveCharacterTextSplitter

st.set_page_config(page_title="Nexxt ANA", page_icon="./logo.jpg")

# Directory where MP3 files are stored
AUDIO_DIR = "./audio/"
logo = "logo.jpg"
fundal = "bg_pic.jpg"

# Function to convert a local image to a base64 string
def load_image_as_base64(image_path):
    image_path = Path(image_path)
    if image_path.exists():
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    else:
        st.error("Image file not found.")
        return None
    
logo_base64 = load_image_as_base64("logo.jpg")



st.markdown(
    """
    <style>
    /* Increase base font size for all text */
    html, body, [class*="css-"] {
        font-size: 1.4em; /* Adjust this value to make text larger or smaller */
    }
    
    /* Style for custom title */
    .title-container {
        font-size: 1.6rem;
        font-weight: bold;
        letter-spacing: -1px;  /* Brings "Asist" and "ANA" closer together */
    }
    .asist {
        color: white; /* White color for Asist */
    }
    .ana {
        color: #FFD700;  /* Yellow color for ANA */
    }

    /* Increase font size for buttons and input elements */
    button, input, select, textarea {
        font-size: 1.4em;
    }

    /* Increase font size for headers */
    h1, h2, h3, h4, h5, h6 {
        font-size: 1.6em;
    }

    /* Customize Streamlit divider to be more prominent */
    .stDivider {
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Display the title with embedded image
if logo_base64:
    st.markdown(
        f"""
        <style>
        .title-container {{
            display: flex;
            align-items: center;
            font-size: 50px;
            font-weight: bold;
            letter-spacing: -1px;
        }}
        .title-container img {{
            height: 60px;
            margin-right: 10px;
        }}
        .asist {{
            color: white;
        }}
        .ana {{
            color: #FFD700;  /* Yellow color for ANA */
        }}
        </style>
        <div class="title-container">
            <img src="data:image/jpeg;base64,{logo_base64}" />
            <span class="asist">Nex</span><span class="ana">X</span><span class="asist">t&nbsp;&nbsp;</span></span><span class="ana">ANA</span>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div class="title-container">
            <img src='./logo.jpg'/>
            <span class="asist">Nexxt </span><span class="ana">ANA</span>
        </div>
        """,
        unsafe_allow_html=True
    )



# Function to list all mp3 files in AUDIO_DIR
def list_audio_files(directory):
    return [f for f in os.listdir(directory) if f.endswith(".mp3") or f.endswith(".wav")]   

def play_audio(file_path):
    audio = AudioSegment.from_mp3(file_path)
    play(audio)


# Set OpenAI API key
openai.api_key = ""

# Set the background image
def set_bg_local_image(image_path):
    """
    A function to set a local image as background.
    """
    image_path = Path(image_path)
    if image_path.exists():
        st.markdown(
            f"""
            <style>
            .stApp {{
                background: url("data:image/jpg;base64,{image_path_to_base64(image_path)}");
                background-size: cover;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("Background image not found!")

def image_path_to_base64(image_path):
    """
    Converts an image file to base64 encoding for use in CSS.
    """
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Set the background using the local image stored in the 'fundal' variable
set_bg_local_image(fundal)

st.divider()

@st.cache_resource(show_spinner=False)
def load_db():
    pdf_link = "merged_output.pdf "
    loader = PyPDFLoader(pdf_link, extract_images=False)
    pages = loader.load_and_split()

    # Split data into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size = 4000,
        chunk_overlap  = 20,
        length_function = len,
        add_start_index = True,
    )
    chunks = text_splitter.split_documents(pages)
    db = Chroma.from_documents(chunks, embedding = OpenAIEmbeddings(openai_api_key=openai.api_key), persist_directory="test_index")
    db.persist()

    # Load the database
    vectordb = Chroma(persist_directory="test_index", embedding_function = OpenAIEmbeddings(openai_api_key=openai.api_key))

    # Load the retriver
    retriever = vectordb.as_retriever(search_kwargs = {"k" : 3})
    return retriever

retriever = load_db()


if "messages" not in st.session_state:
    st.session_state.messages = []

container = st.container(border=True)
st.header("Alege o înregistrare")

# List available MP3 files for selection
audio_files = list_audio_files(AUDIO_DIR)
selected_file = st.selectbox("", audio_files)

# Set file path for the selected file
file_path = os.path.join(AUDIO_DIR, selected_file)
    
st.audio(file_path, format='audio/mp3', start_time=0)

if st.button("Soluții"):
    st.session_state.messages = []
    user_input = ""
    if file_path:
        text = transcribe_audio(file_path)
        user_input = summarize_text(text)
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            # Display all messages in the chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            # Find the index where "Probleme:" is located and split the text after it
            if "Probleme:" in user_input:
                # Extract everything after "Probleme:"
                problems_section = user_input.split("Probleme:")[1].strip()
                # Split the section into individual problems (lines)
                problems_list = [problem.strip() for problem in problems_section.split("\n") if problem.strip()]
            else:
                problems_list = []

            # Process each problem one by one
            for problem in problems_list:
                # Add each problem as a separate message in chat history
                st.session_state.messages.append({"role": "user", "content": f"Problema: {problem}"})
                
                context = retriever.get_relevant_documents(problem)

                # Retrieve relevant document content if a document has been uploaded
                # sources = retriever.invoke(problem)
                # context = ""
                # for doc in sources:
                    # context += doc.page_content + "\n\n"
                # contextul reprezinta sumarul conversatiei client-operator
                augmented_user_input = f'Context: """{context}"""\n\nÎntrebare: {problem}\n'

                # Chat with GPT using augmented input
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[ 
                        {"role": "system", "content": "Esti un asistent virtual de ajutor pentru un operator call center al unei bănci."
                                                        " Foloseste textul care este delimitat de ghilimele triple "
                                                        " pentru a ajuta operatorul și"
                                                        " a oferi informatii relevante. Daca nu poți găsi un raspuns in articole,"
                                                        " raspunde cu 'Nu pot oferi informații despre acest subiect'."
                                                        "Raspunsul oferit nu trebuie sa fie introdus intre niciun fel de ghilimele."},
                        {"role": "user", "content": augmented_user_input}
                    ]
                )
                
                response_text = response.choices[0].message.content.strip()
                
                # Add assistant's response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
                with open("rag_output.txt", "a", encoding="utf-8") as file:
                    file.write(problem + "\n" + response_text + "\n")

                # Display the updated chat history
                for message in st.session_state.messages[-2:]:  # Only show the current problem and response
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])