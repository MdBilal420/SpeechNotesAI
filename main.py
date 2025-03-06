import streamlit as st
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource
)
import json
import asyncio
import os
import groq

st.title("SpeechNotes AI")
st.write("Upload your audio file below")

# Get Deepgram API Key from environment variable or user input
DEEPGRAM_API_KEY = st.sidebar.text_input("Enter your Deepgram API Key", type="password")
# Get Groq API Key from user input
GROQ_API_KEY = st.sidebar.text_input("Enter your Groq API Key", type="password")

# Initialize Groq client
if GROQ_API_KEY:
    groq_client = groq.Groq(api_key=GROQ_API_KEY)
else:
    st.sidebar.warning("Please enter your Groq API Key to enable note generation.")

# Create a file uploader widget that accepts audio files
audio_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'ogg'])
   

async def transcribe_audio(file_path):
    try:
        # Initialize the Deepgram client
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        
        # Open the audio file
        with open(file_path, 'rb') as buffer_data:
            # Configure transcription options
            payload = { 'buffer': buffer_data }
            options = PrerecordedOptions(
                smart_format=True, model="nova-2", language="en-US"
            )
            
            # Send the audio to Deepgram and get the response (using rest instead of prerecorded)
            response = deepgram.listen.rest.v('1').transcribe_file(payload, options)
            return response.results.channels[0].alternatives[0].transcript
    except Exception as e:
        return f"Error during transcription: {str(e)}"

def generate_bullet_summary(transcript):
    if not GROQ_API_KEY:
        return "Error: Please enter your Groq API Key in the sidebar to generate summaries."
        
    try:
        # Define the prompt for generating bullet point summaries
        prompt = f"""
        Create a concise bullet point summary of the following transcript.
        Focus on key points, main ideas, and important details.
        Format as bulleted list with clear, concise points.
        
        Transcript:
        {transcript}
        """
        
        # Call Groq API to generate the summary
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Using newer Llama 3.3 70B model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise, well-organized bullet point summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more focused responses
            max_tokens=1024
        )
        
        # Extract the summary from the response
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# Display file information if a file is uploaded
if audio_file is not None:
    st.write("File Details:")
    st.write(f"Filename: {audio_file.name}")
    
    # Display the audio player
    st.audio(audio_file)
    
    # Save the uploaded file temporarily
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_file.getbuffer())
    
    # Create columns for the buttons
    col1, col2 = st.columns(2)
    
    # Add a transcribe button with styling
    with col1:
        transcribe_button = st.button(
            "🎤 Transcribe Audio", 
            use_container_width=True,
            type="primary",
            disabled=not DEEPGRAM_API_KEY
        )
    
    # Add the Generate Notes button with styling
    with col2:
        generate_notes_button = st.button(
            "📝 Generate Notes", 
            use_container_width=True,
            type="secondary",
            disabled=not GROQ_API_KEY
        )
    
    # Handle transcribe button click
    if transcribe_button:
        with st.spinner("Transcribing..."):
            # Run the async function
            transcript = asyncio.run(transcribe_audio("temp_audio.wav"))
            
            # Store the transcript in session state for later use
            st.session_state.transcript = transcript
            st.session_state.last_action = 'transcribe'
            
            # Force a rerun to update the UI
            st.rerun()
    
    # Handle generate notes button click
    if generate_notes_button:
        if not GROQ_API_KEY:
            st.error("Please enter your Groq API Key in the sidebar to generate summaries.")
        elif 'transcript' in st.session_state and st.session_state.transcript:
            with st.spinner("Generating bullet point summary..."):
                summary = generate_bullet_summary(st.session_state.transcript)
                
                # Store the summary in session state
                st.session_state.summary = summary
                st.session_state.last_action = 'generate_summary'
                
                # Force a rerun to update the UI
                st.rerun()
        else:
            st.warning("Please transcribe the audio first before generating notes.")
    
    # Create tabs for displaying content
    if 'transcript' in st.session_state or 'summary' in st.session_state:
        # Set default tab index based on latest action
        default_tab_index = 0
        if 'last_action' in st.session_state:
            if st.session_state.last_action == 'generate_summary':
                default_tab_index = 1
        
        # Create tabs with the determined default tab
        tab1, tab2 = st.tabs(["📝 Transcription", "📊 Bullet Points"])
        
        # Display content in tabs if available
        with tab1:
            if 'transcript' in st.session_state:
                st.subheader("Transcription:")
                st.markdown("---")
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50;">
                        {st.session_state.transcript}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add download button for transcript
                transcript_bytes = st.session_state.transcript.encode()
                st.download_button(
                    label="Download Transcript",
                    data=transcript_bytes,
                    file_name="transcript.txt",
                    mime="text/plain"
                )
            else:
                st.info("No transcript available yet. Click 'Transcribe Audio' to generate one.")
        
        with tab2:
            if 'summary' in st.session_state:
                st.subheader("Bullet Point Summary:")
                st.markdown("---")
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;">
                        {st.session_state.summary}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add download button for summary
                summary_bytes = st.session_state.summary.encode()
                st.download_button(
                    label="Download Summary",
                    data=summary_bytes,
                    file_name="summary.txt",
                    mime="text/plain"
                )
            else:
                st.info("No summary available yet. Click 'Generate Notes' to create one.")
    
    # Clean up the temporary file
    if os.path.exists("temp_audio.wav"):
        os.remove("temp_audio.wav")
elif audio_file is None:
    st.info("Please upload an audio file to get started.")

# Display warnings for missing API keys
if not DEEPGRAM_API_KEY:
    st.sidebar.warning("⚠️ Deepgram API Key is required for transcription.")
if not GROQ_API_KEY:
    st.sidebar.warning("⚠️ Groq API Key is required for generating notes.")
