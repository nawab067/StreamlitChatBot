import streamlit as st
from streamlit_option_menu import option_menu
import google.generativeai as gen_ai

GOOGLE_API_KEY = st.secrets["google"]["api_key"]

if not GOOGLE_API_KEY:
    st.error("Google API key not found.")
else:
    gen_ai.configure(api_key=GOOGLE_API_KEY)

    model = gen_ai.GenerativeModel("gemini-2.0-flash")

    def map_role(role):
        return "assistant" if role == "model" else role

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    st.set_page_config(page_title="Start with Gemini", page_icon="🧠", layout="centered")
    st.title("Start with Gemini")

    for message in st.session_state.chat_session.history:
        with st.chat_message(map_role(message.role)):
            st.markdown(message.parts[0].text)

    user_input = st.chat_input("Type Your Query Here.......")
    if user_input:
        st.chat_message("user").markdown(user_input)
        response = st.session_state.chat_session.send_message(user_input)
        with st.chat_message("assistant"):
            st.markdown(response.text)
