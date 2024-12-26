import streamlit as st
import cv2
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
    # Using pydub to extract audio from the video
    audio = AudioSegment.from_file(video_path)
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    audio.export(audio_file, format="wav")
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
    # Using OpenCV to read and process the video file
    video = cv2.VideoCapture(video_path)
    
    # Get the FPS (frames per second) of the video
    fps = video.get(cv2.CAP_PROP_FPS)
    
    # Calculate the frame positions for start and end time
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    
    # Create the output path for the highlight video
    highlight_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Video codec
    
    # Prepare the video writer
    out = cv2.VideoWriter(highlight_path, fourcc, fps, (int(video.get(3)), int(video.get(4))))
    
    # Read and write frames to create the highlight clip
    frame_count = 0
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        if start_frame <= frame_count <= end_frame:
            out.write(frame)
        frame_count += 1
        if frame_count > end_frame:
            break
    
    # Release resources
    video.release()
    out.release()
    return highlight_path

# Process the uploaded video if any
if uploaded_video:
    video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    with open(video_path, "wb") as f:
        f.write(uploaded_video.read())
    
    # Show the uploaded video
    st.video(video_path)

    # Display video details
    video = cv2.VideoCapture(video_path)
    duration = video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS)
    st.write(f"Duration: {duration:.2f} seconds")
    st.write(f"Resolution: {int(video.get(3))}x{int(video.get(4))}")

    # Get the start and end times for the highlight
    st.header("Create Highlight")
    start_time = st.number_input("Start Time (seconds)", 0, int(duration), 0)
    end_time = st.number_input("End Time (seconds)", 0, int(duration), 10)

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
