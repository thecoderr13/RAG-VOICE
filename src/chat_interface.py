import streamlit as st
import speech_recognition as sr
from src.api_utils import get_api_response

def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Speak now... (5 seconds)")
        audio = recognizer.listen(source, timeout=5)
    try:
        text = recognizer.recognize_google(audio, language="en-US")
        st.write(f"Recognized: {text}")
        return text
    except sr.UnknownValueError:
        st.write("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError as e:
        st.write(f"Request error: {e}")
        return None

def display_chat_interface():
    # Initialize session state variables if not present
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

    # Voice and text input section
    if st.button("Voice Input"):
        prompt = get_voice_input()
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
                    st.error("Failed to get a response from the API. Please try again.")

    # Handle new user input
    if prompt := st.chat_input("Query:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        # Get API response
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
                st.error("Failed to get a response from the API. Please try again.")