import streamlit as st
from streamlit_option_menu import option_menu
import google.generativeai as gen_ai
import speech_recognition as sr
from gtts import gTTS
import tempfile
import time

st.set_page_config(page_title="Start with Gemini",
                   page_icon="🧠",
                   layout="centered")

GOOGLE_API_KEY = st.secrets["google"]["api_key"]

if not GOOGLE_API_KEY:
    st.error("Google API key not found in secrets.toml.")
else:
    gen_ai.configure(api_key=GOOGLE_API_KEY)
    model = gen_ai.GenerativeModel("gemini-2.0-flash")

    selected_app = st.sidebar.radio("Select Mode", ["ChatBot", "Gemini"])

    if selected_app == "ChatBot":
        # --- Chat role mapping ---
        def map_role(role):
            return "assistant" if role == "model" else role

        # --- Session state for chat history ---
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[])

        # --- Streamlit Page Setup ---
        st.title("💬 Chat with Gemini")

        # --- Display Chat History ---
        for message in st.session_state.chat_session.history:
            with st.chat_message(map_role(message.role)):
                st.markdown(message.parts[0].text)

        # --- Input from user ---
        user_input = st.chat_input("Type your query here...")

        if user_input:
            st.chat_message("user").markdown(user_input)
            response = st.session_state.chat_session.send_message(user_input)
            with st.chat_message("assistant"):
                st.markdown(response.text)

    elif selected_app == "Gemini":
        st.title("🎙️ Gemini Voice Assistant")
        r = sr.Recognizer()

        # Voice input
        def get_voice_input():
            with sr.Microphone() as source:
                st.info("🎤 Listening... Please speak.")
                audio = r.listen(source)
                try:
                    return r.recognize_google(audio, language="en-in")
                except sr.UnknownValueError:
                    return "Sorry, I didn't catch that."

        # Process user input and generate response
        def process_input(prompt):
            with st.spinner("💡 Gemini is thinking..."):
                response = model.generate_content(
                    prompt,
                    generation_config=gen_ai.GenerationConfig(
                        temperature=0.7,
                        top_p=1,
                        max_output_tokens=256
                    )
                )
                return response.text

        # Text-to-speech
        def speak(text):
            sentences = text.split('. ')
            for sentence in sentences:
                if sentence.strip() == "":
                    continue
                tts = gTTS(text=sentence, lang='en')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    st.audio(fp.name, format="audio/mp3")
                    time.sleep(0.5)

        # Main app logic
        if st.button("🎤 Talk to Gemini"):
            user_input = get_voice_input()
            if user_input.strip() != "":
                response_text = process_input(user_input)
                speak(response_text)
                st.markdown("## 🤖 Gemini's Response:")
                st.success(response_text)
