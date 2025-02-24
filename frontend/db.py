import streamlit as st
import yt_dlp
import re
import bcrypt
import logging
from pymongo import MongoClient
from datetime import datetime
from backend_python import (
    convert_mp3_to_wav,
    load_vosk_model,
    transcribe_audio,
    format_transcriptions
)

# --- Configure Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# --- Configure Secrets ---
MONGO_URI = "mongodb+srv://yashadmin:<yashpasss123>@cliphop1.uif14.mongodb.net/?retryWrites=true&w=majority&appName=cliphop1"

VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"  

# --- Database Functions ---
def init_db():
    client = MongoClient(MONGO_URI)
    db = client["clipusers"]
    return db.users

def create_user(email, password, username):
    users = init_db()
    if users.find_one({"email": email}):
        return False
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_data = {"email": email, "username": username, "password": hashed, "created_at": datetime.utcnow()}
    users.insert_one(user_data)
    return True

def verify_user(email, password):
    users = init_db()
    user = users.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return user
    return None

# --- Authentication Pages ---
def show_login():
    with st.form("Login"):
        st.subheader("Login to Cliphop")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            user = verify_user(email, password)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = user["email"]
                st.session_state["username"] = user.get("username", "User")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

def show_signup():
    with st.form("Signup"):
        st.subheader("Create New Account")
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Create Account")
        if submitted:
            if create_user(email, password, username):
                st.success("Account created! Please login")
                st.session_state["show_login"] = True
            else:
                st.error("Email already exists")

# --- YouTube Video Extraction ---
def extract_video_id(url):
    patterns = [
        r"^https?://(?:www\.)?youtube\.com/watch\?v=([^&]+)",
        r"^https?://youtu\.be/([^?]+)",
        r"^https?://(?:www\.)?youtube\.com/embed/([^/?]+)"
    ]
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    return None

# --- Main Function ---
def main():
    st.set_page_config(page_title="Cliphop", page_icon="🎵", layout="wide")

    # Authentication Handling
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.image("logoblkrmbg.png", width=150)
        col1, col2 = st.columns(2)
        with col1:
            if "show_login" not in st.session_state:
                st.session_state.show_login = True
            if st.session_state.show_login:
                show_login()
                if st.button("Sign Up"):
                    st.session_state.show_login = False
            else:
                show_signup()
                if st.button("Login"):
                    st.session_state.show_login = True
        return  # Stop execution if not logged in

    # Sidebar with Logout Option
    with st.sidebar:
        st.write(f"Logged in as {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.clear()
            st.experimental_rerun()

    # Main Content
    st.markdown("<h1 style='color: #2b3a42;'>Enhance Your Studies with AI</h1>", unsafe_allow_html=True)
    
    video_url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/...")
    
    if st.button("⏬ Load Your Lectures"):
        if video_url:
            try:
                with st.spinner("🔄 Processing... Please wait"):
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": "./%(title)s.%(ext)s",
                        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_url, download=True)
                        mp3_path = info['requested_downloads'][0]['filepath']
                        st.toast(f"🎉 Successfully downloaded: {info['title']}.mp3", icon="✅")

                        # Convert to WAV and Transcribe
                        with st.spinner("🔊 Running Extractor ... 💾"):
                            progress_bar = st.progress(0)
                            wav_data, sr = convert_mp3_to_wav(mp3_path)
                            model = load_vosk_model(VOSK_MODEL_PATH)

                            def update_progress(percent_complete):
                                progress_bar.progress(percent_complete)
                            
                            transcripts = transcribe_audio(wav_data, sr, model, progress_callback=update_progress)
                            progress_bar.progress(100)

                            formatted = format_transcriptions(transcripts)
                            st.session_state.transcription = formatted
                            st.session_state.audio_title = info['title']

                            with open("data.txt", "w") as file:
                                file.write(st.session_state.transcription)

                            st.toast("✅ Transcription completed!", icon="✅")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please provide a valid YouTube URL first")

# --- Run the Application ---
if __name__ == "__main__":
    main()
