import streamlit as st
import yt_dlp
import re
from backend_python import (
    convert_mp3_to_wav,
    load_vosk_model,
    transcribe_audio,
    format_transcriptions
)
import logging

# Configure model path (preferably in secrets)
VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"  # Update with your actual path


# Add this logging configuration (in your main function or at top)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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

# Add Font Awesome CSS
st.markdown(
    """<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">""",
    unsafe_allow_html=True
)


# Custom CSS Styling
st.markdown(
    """
    <style>
    /* Main container styling */

    .main {
        background-color: white ;
        
    }
    

    [data-testid="stSidebar"] button {
        color: black !important;
    }

    /* Hover effects */
    [data-testid="stSidebar"] button:hover {
        color: #ffffff !important;
        background-color: #ff6b6b !important;
    }


    
    /* Main content area */
    .main-content {
        margin-right: 320px !important;
        padding: 20px;
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Video container */
    .video-container {
        position: relative;
        padding-bottom: 56.25%;
        height: 0;
        overflow: hidden;
        border-radius: 15px;
        margin: 20px 0;
    }
    
    .video-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
    
    /* Download button styling */
    .download-btn {
        background: linear-gradient(45deg, #ff4b4b, #ff6b6b) !important;
        color: white !important;
        border: none !important;
        padding: 12px 24px !important;
        border-radius: 25px !important;
        font-weight: 600 !important;
        width: 100%;
        margin-top: 20px;
    }

/* Right Sidebar Styling */
.right-sidebar {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-left: 20px;
}

.right-sidebar h3 {
    color: #2b3a42;
    font-size: 1.2rem;
    margin-bottom: 15px;
}

.right-sidebar h4 {
    color: #3c5c6e;
    font-size: 1rem;
    margin: 15px 0 10px;
}

.right-sidebar p {
    font-size: 0.9rem;
    line-height: 1.4;
    margin: 8px 0;
}

    </style>
    """,
    unsafe_allow_html=True,
)
# Replace the existing sidebar code with this:
with st.sidebar:

    st.image("logoblkrmbg.png", width=150)
    
    st.button("🏠 Dashboard")
    st.button("📊 Analytics")
    st.button("⚙️ Settings")
    
    # Add this CSS to your existing style block
    st.markdown("""
    <style>
    .sidebar-content {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar-content h3 {
        color: #2b3a42 !important;
        font-size: 1.2rem;
        margin-bottom: 15px;
    }
    
    .sidebar-content h4 {
        color: #3c5c6e !important;
        font-size: 1rem;
        margin: 15px 0 10px;
    }
    
    .sidebar-content p {
        font-size: 0.9rem !important;
        line-height: 1.4;
        margin: 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Modified user profile section
    st.markdown("""
    <div class="sidebar-content">
        <h3>👤 User Profile</h3>
        <p>🌟 Premium Member</p>
        <p>📧 user@example.com</p>
        <p>💾 Storage: 15.2/50 GB</p>
        <hr>
        <h4>📊 Statistics</h4>
        <p>▶️ Total Downloads: 127</p>
        <p>⭐ User Rating: 4.8/5</p>
        <hr>
        <h4>📅 Recent Activity</h4>   
        <p>✅ Downloaded "Summer Mix 2023" : 2 hours ago</p>
        <p>⚠️ Failed download attempt : 5 hours ago</p>
        <hr>
        <h4>🔔 Notifications</h4>
        <p>📢 New feature: Playlist support!</p>
        <p>🔄 System maintenance: June 15</p>
    </div>
    """, unsafe_allow_html=True)
    
# Main Content Area
main_col, right_sidebar = st.columns([3, 1])

with main_col:
    # Create a  text input field

    st.markdown("<h1 style='color: #2b3a42;'>Enhance Your studies with AI</h1>", 
                unsafe_allow_html=True)
    
    # Video Preview Section
    if 'video_url' in st.session_state and st.session_state.video_url:
        video_id = extract_video_id(st.session_state.video_url)
        if video_id:
            st.markdown(
                f'<div class="video-container">'
                f'<iframe src="https://www.youtube.com/embed/{video_id}" '
                f'frameborder="0" allowfullscreen></iframe></div>',
                unsafe_allow_html=True
            )
        else:
            st.error("⚠️ Please enter a valid YouTube URL")

    # URL Input and Download Section
    video_url = st.text_input("Enter YouTube URL:", 
                             placeholder="https://www.youtube.com/...", 
                             key="video_url",
                             label_visibility="collapsed")
    
    
    if st.button("⏬ Load Your Lectures", key="download_btn", use_container_width=True):
        if video_url:
            try:
                with st.spinner("🔄 Processing... Please wait"):
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": "./%(title)s.%(ext)s",
                        "postprocessors": [{
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }],
                    }
                
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_url, download=True)
                        mp3_path = info['requested_downloads'][0]['filepath']
                        st.toast(f"🎉 Successfully downloaded: {info['title']}.mp3", icon="✅")
                    
                    # Transcription process
                        with st.spinner("🔊 Running Extractor ... 💾"):
                        # Initialize progress bar
                            progress_bar = st.progress(0)
                        
                        # Convert and transcribe with progress updates
                            wav_data, sr = convert_mp3_to_wav(mp3_path)
                            model = load_vosk_model(VOSK_MODEL_PATH)
                        
                        # Create progress callback
                            def update_progress(percent_complete):
                                progress_bar.progress(percent_complete)
                            
                            transcripts = transcribe_audio(
                                wav_data, 
                                sr, 
                                model,
                                progress_callback=update_progress
                            )
                        
                        # Final 100% update
                            progress_bar.progress(100)
                        
                        # Format and store results
                            formatted = format_transcriptions(transcripts)
                            st.session_state.transcription = formatted
                            st.session_state.audio_title = info['title']
                            #print(st.session_state.transcription)
                            with open("data.txt", "w") as file:
                                file.write(st.session_state.transcription)
                            st.toast("✅ Transcription completed!", icon="✅")
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please provide a valid YouTube URL first")

# Footer
st.markdown("""
<div style= text-align: center; padding: 20px; color: #666; '>
    <p>© 2024 AudioStream Pro | 📧 support@audiostream.com | 🔒 SSL Secured Connection</p>
    <div style='margin-top: 10px;'>
        <span style='margin: 0 10px;'>📘 Terms of Service</span>
        <span style='margin: 0 10px;'>🔏 Privacy Policy</span>
        <span style='margin: 0 10px;'>📞 Support</span>
    </div>
</div>
""", unsafe_allow_html=True)
