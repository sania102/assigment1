import streamlit as st
from moviepy.editor import VideoFileClip
import os
import time
import speech_recognition as sr
from pydub import AudioSegment
import tempfile

st.title("Video Highlight Generator")

# Upload video file
uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])

# Function to extract audio from video
def extract_audio_from_video(video_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    audio.write_audiofile(audio_file)
    return audio_file

# Function to transcribe audio
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Audio could not be understood."
    except sr.RequestError as e:
        return f"Error with Google API: {e}"

# Function to create the video highlight
def create_highlight_video(video_path, start_time, end_time):
    video = VideoFileClip(video_path)
    highlight_clip = video.subclip(start_time, end_time)
    highlight_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    highlight_clip.write_videofile(highlight_path, codec="libx264")
    return highlight_path

# Process the uploaded video if any
if uploaded_video:
    video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    with open(video_path, "wb") as f:
        f.write(uploaded_video.read())
    
    # Show the uploaded video
    st.video(video_path)

    # Display video details
    video_clip = VideoFileClip(video_path)
    st.write(f"Duration: {video_clip.duration} seconds")
    st.write(f"Resolution: {video_clip.size[0]}x{video_clip.size[1]}")

    # Get the start and end times for the highlight
    st.header("Create Highlight")
    start_time = st.number_input("Start Time (seconds)", 0, int(video_clip.duration), 0)
    end_time = st.number_input("End Time (seconds)", 0, int(video_clip.duration), 10)

    # Create highlight video when button is clicked
    if st.button("Create Highlight"):
        with st.spinner('Processing your highlight video...'):
            highlight_path = create_highlight_video(video_path, start_time, end_time)
            
            st.video(highlight_path)
            with open(highlight_path, "rb") as file:
                st.download_button(
                    label="Download Highlight Video",
                    data=file,
                    file_name="highlight_video.mp4",
                    mime="video/mp4"
                )
        
        # Transcription section
        st.header("Transcription")
        with st.spinner('Extracting and transcribing audio...'):
            audio_file = extract_audio_from_video(video_path)
            transcription = transcribe_audio(audio_file)
            st.text_area("Transcription", transcription, height=200)
            
            # Provide download link for the audio
            with open(audio_file, "rb") as file:
                st.download_button(
                    label="Download Audio",
                    data=file,
                    file_name="audio.wav",
                    mime="audio/wav"
                )

    # Download link for the original video
    with open(video_path, "rb") as file:
        st.download_button(
            label="Download Original Video",
            data=file,
            file_name="uploaded_video.mp4",
            mime="video/mp4"
        )
import os
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import moviepy.editor as mp
except ImportError:
    install("moviepy")

try:
    from pydub import AudioSegment
except ImportError:
    install("pydub")

try:
    import speech_recognition as sr
except ImportError:
    install("SpeechRecognition")
