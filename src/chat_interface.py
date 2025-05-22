import streamlit as st
import speech_recognition as sr
from src.api_utils import get_api_response
import tempfile
import os



# === Audio transcription ===
def transcribe_audio_file(uploaded_file):
    recognizer = sr.Recognizer()

    # Save uploaded WAV file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        temp_wav.write(uploaded_file.read())
        temp_wav_path = temp_wav.name

    # Transcribe the WAV file
    with sr.AudioFile(temp_wav_path) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)

    return text


def display_chat_interface():
    
    st.markdown("<h2 style='color: red;'>Voice/Text Chat Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: orange;'>Upload Audio or Type a Query</h4>", unsafe_allow_html=True)


    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "model" not in st.session_state:
        st.session_state.model = "gemini-1.5-flash"

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

   
    prompt = None

    # === Upload audio file (.wav or .mp3) ===
    uploaded_audio = st.file_uploader("Upload a .wav file", type=["wav"])
    if uploaded_audio:
        with st.spinner("Transcribing audio..."):
            prompt = transcribe_audio_file(uploaded_audio)

    # === Text input ===
    if text_input := st.chat_input("Type your query here"):
        prompt = text_input

    # === Process prompt and generate response ===
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Generating response..."):
            response = get_api_response(prompt, st.session_state.session_id, st.session_state.model)

        if response:
            st.session_state.session_id = response.get('session_id')
            st.session_state.messages.append({"role": "assistant", "content": response['answer']})

            with st.chat_message("assistant"):
                st.markdown(response['answer'])

            with st.expander("Details"):
                st.subheader("Generated Answer")
                st.code(response['answer'])
                st.subheader("Model Used")
                st.code(response['model'])
                st.subheader("Session ID")
                st.code(response['session_id'])
        else:
            st.error("Failed to get a response from the API.")
