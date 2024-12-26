import streamlit as st
import cv2
import os
import io
import time
import speech_recognition as sr
from pydub import AudioSegment
import ffmpeg
from io import BytesIO

st.title("Video Highlight Generator")

# Upload video file
uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])

# Function to extract audio from video
def extract_audio_from_video(video_file):
    # Save video to a temporary in-memory file
    video_file.seek(0)  # Reset file pointer to the beginning
    video_path = '/tmp/video.mp4'  # Temp path for the video file in memory
    with open(video_path, 'wb') as f:
        f.write(video_file.read())

    # Use ffmpeg to extract audio
    audio_path = '/tmp/audio.wav'  # Temp path for the audio file
    ffmpeg.input(video_path).output(audio_path).run()

    # Load and return the audio file
    return audio_path

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
def create_highlight_video(video_file, start_time, end_time):
    # Read the uploaded video file
    video_file.seek(0)
    video_path = '/tmp/video.mp4'
    with open(video_path, 'wb') as f:
        f.write(video_file.read())

    # Use OpenCV to read the video and extract the highlight clip
    video = cv2.VideoCapture(video_path)
    video_fps = video.get(cv2.CAP_PROP_FPS)  # Corrected this line
    start_frame = int(start_time * video_fps)
    end_frame = int(end_time * video_fps)
    
    # Create the output video file for the highlight
    highlight_path = '/tmp/highlight.mp4'  # Temp path for highlight
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(highlight_path, fourcc, video_fps, (int(video.get(3)), int(video.get(4))))
    
    # Write the frames to the new video
    video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    while video.isOpened():
        ret, frame = video.read()
        if not ret or video.get(cv2.CAP_PROP_POS_FRAMES) > end_frame:
            break
        out.write(frame)
    
    video.release()
    out.release()
    return highlight_path

# Process the uploaded video if any
if uploaded_video:
    # Show the uploaded video
    st.video(uploaded_video)

    # Open the video with OpenCV to calculate duration
    video_path = '/tmp/video.mp4'
    with open(video_path, 'wb') as f:
        f.write(uploaded_video.read())
    
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)  # Corrected this line
    video_duration = total_frames / fps
    video.release()

    # Get the start and end times for the highlight
    st.header("Create Highlight")
    start_time = st.number_input("Start Time (seconds)", 0, int(video_duration), 0)
    end_time = st.number_input("End Time (seconds)", 0, int(video_duration), 10)

    # Create highlight video when button is clicked
    if st.button("Create Highlight"):
        with st.spinner('Processing your highlight video...'):
            highlight_path = create_highlight_video(uploaded_video, start_time, end_time)
            
            # Display the highlight video
            st.video(highlight_path)

            # Provide download link for the highlight
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
            audio_file = extract_audio_from_video(uploaded_video)
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
