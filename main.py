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
import re

st.title("SpeechNotes AI")
st.write("Upload your audio file below")

# Get Deepgram API Key from environment variable or user input
DEEPGRAM_API_KEY = st.sidebar.text_input("Enter your Deepgram API Key", type="password",value="f82b963c2c49744b16b32298e89b9f8eca974095")
# Get Groq API Key from user input
GROQ_API_KEY = st.sidebar.text_input("Enter your Groq API Key", type="password",value="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")

# Initialize Groq client
if GROQ_API_KEY:
    groq_client = groq.Groq(api_key=GROQ_API_KEY)
else:
    st.sidebar.warning("Please enter your Groq API Key to enable note generation.")

# Create a file uploader widget that accepts audio files
audio_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'ogg'])

# Create tabs for the interface
tabs = st.tabs(["📝 Transcription", "📊 Bullet Points", "🤖 Talk to Tutor", "📝 Test Yourself"])

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
        
        # Display content in tabs if available
        with tabs[0]:  # Transcription tab
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
        
        with tabs[1]:  # Bullet Points tab
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
        
        with tabs[2]:  # Talk to Tutor tab
            st.subheader("Ask Questions About the Transcription")
            st.markdown("---")
            
            # Create a container for the entire chat interface
            chat_container = st.container()
            
            # Create a container for the input at the bottom
            input_container = st.container()
            
            # Initialize chat history in session state if it doesn't exist
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            # Check if transcription exists
            if 'transcript' not in st.session_state:
                with chat_container:
                    st.info("Please transcribe the audio first before chatting with the tutor.")
            else:
                # Chat input (at the bottom)
                with input_container:
                    # Add a button to clear chat history
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("Clear Chat", key="clear_chat", use_container_width=True):
                            st.session_state.chat_history = []
                            st.rerun()
                    
                    # Chat input
                    user_question = st.chat_input("Ask a question about the transcription...")
                
                # Display chat messages in a scrollable container
                with chat_container:
                                      
                    # Display chat messages
                    if not st.session_state.chat_history:
                        st.markdown("<p style='color: #888; text-align: center; margin-top: 150px;'>Ask a question to start the conversation</p>", unsafe_allow_html=True)
                    else:
                        for message in st.session_state.chat_history:
                            with st.chat_message(message["role"]):
                                st.write(message["content"])
                    
                    # Close the chat-history div
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if user_question:
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                
                # Process the question with Groq
                with st.spinner("Thinking..."):
                    try:
                        response = groq_client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": f"""You are a Socratic tutor. Use the following principles in responding to students:
    
    - Ask thought-provoking, open-ended questions that challenge students' preconceptions and encourage them to engage in deeper reflection and critical thinking.
    - Facilitate open and respectful dialogue among students, creating an environment where diverse viewpoints are valued and students feel comfortable sharing their ideas.
    - Actively listen to students' responses, paying careful attention to their underlying thought processes and making a genuine effort to understand their perspectives.
    - Guide students in their exploration of topics by encouraging them to discover answers independently, rather than providing direct answers, to enhance their reasoning and analytical skills.
    - Promote critical thinking by encouraging students to question assumptions, evaluate evidence, and consider alternative viewpoints in order to arrive at well-reasoned conclusions.
    - Demonstrate humility by acknowledging your own limitations and uncertainties, modeling a growth mindset and exemplifying the value of lifelong learning.

Base your responses on the following transcription content. Your goal is not to simply provide answers, but to help the student think critically about the material through Socratic questioning.

Transcription: {st.session_state.transcript}
"""},
                                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
                            ],
                            temperature=0.3,
                            max_tokens=1024
                        )
                        
                        assistant_response = response.choices[0].message.content
                        
                        # Add assistant response to chat history
                        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                    except Exception as e:
                        error_message = f"Error generating response: {str(e)}"
                        st.session_state.chat_history.append({"role": "assistant", "content": error_message})
                        
                        # Rerun to update the chat display
                        st.rerun()
    
    with tabs[3]:  # Test Yourself tab
        st.subheader("Test Your Knowledge")
        st.markdown("---")
        
        # Check if transcription exists
        if 'transcript' not in st.session_state:
            st.info("Please transcribe the audio first before generating a quiz.")
        else:
            # Initialize quiz state if not already done
            if 'quiz_generated' not in st.session_state:
                st.session_state.quiz_generated = False
            
            if 'quiz_questions' not in st.session_state:
                st.session_state.quiz_questions = []
                
            if 'current_question' not in st.session_state:
                st.session_state.current_question = 0
                
            if 'score' not in st.session_state:
                st.session_state.score = 0
                
            if 'quiz_completed' not in st.session_state:
                st.session_state.quiz_completed = False
            
            # Button to generate quiz
            if not st.session_state.quiz_generated and not st.session_state.quiz_completed:
                if st.button("Generate Quiz", key="generate_quiz", use_container_width=True, type="primary"):
                    with st.spinner("Creating quiz questions..."):
                        try:
                            # Generate quiz questions using Groq
                            response = groq_client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[
                                    {"role": "system", "content": "You are a quiz creator of highly diagnostic quizzes. You will make good low-stakes tests and diagnostics"},
                                    {"role": "user", "content": f"""
                                    Create a quiz with 5 multiple-choice questions based on the following transcription.
                                    The questions should be highly relevant and go beyond just facts. 
                                    Multiple choice questions should include plausible, 
                                    competitive alternate responses and should not include an "all of the above option." 
                                    For each question:
                                    1. Provide a clear question
                                    2. Give 4 possible answers (A, B, C, D)
                                    3. Indicate the correct answer
                                    
                                    Format your response as a JSON array with this structure:
                                    [
                                        {{
                                            "question": "Question text here?",
                                            "options": ["Option A", "Option B", "Option C", "Option D"],
                                            "correct_answer": 0  // Index of correct answer (0-3)
                                        }},
                                        // more questions...
                                    ]
                                    
                                    Transcription:
                                    {st.session_state.transcript}
                                    """
                                    }
                                ],
                                temperature=0.3,
                                max_tokens=2048
                            )
                            
                            # Parse the response to get quiz questions
                            response_content = response.choices[0].message.content
                            
                            try:
                                # First, try to find JSON in code blocks
                                json_match = re.search(r'```(?:json)?\n?([\s\S]*?)\n?```', response_content)
                                
                                if json_match:
                                    # Found JSON in code block
                                    json_str = json_match.group(1).strip()
                                else:
                                    # Try to find array directly
                                    array_match = re.search(r'\[\s*\{[\s\S]*\}\s*\]', response_content)
                                    if array_match:
                                        json_str = array_match.group(0)
                                    else:
                                        # Just use the whole response as a fallback
                                        json_str = response_content
                                
                                # Clean up the JSON string
                                # Remove any trailing commas before closing brackets (common JSON error)
                                json_str = re.sub(r',\s*}', '}', json_str)
                                json_str = re.sub(r',\s*]', ']', json_str)
                                
                                # Fix missing commas between objects
                                json_str = re.sub(r'}\s*{', '},{', json_str)
                                
                                # Ensure it's a proper array
                                if not json_str.strip().startswith('['):
                                    json_str = '[' + json_str + ']'
                                if not json_str.strip().endswith(']'):
                                    json_str = json_str + ']'
                                
                                # Parse the JSON
                                import json
                                st.session_state.quiz_questions = json.loads(json_str)
                                
                                # Validate the quiz questions format
                                for q in st.session_state.quiz_questions:
                                    if not all(k in q for k in ["question", "options", "correct_answer"]):
                                        raise ValueError("Quiz question is missing required fields")
                                    if not isinstance(q["options"], list) or len(q["options"]) < 2:
                                        raise ValueError("Quiz options must be a list with at least 2 items")
                                    if not isinstance(q["correct_answer"], int):
                                        # Try to convert to int if it's a string number
                                        try:
                                            q["correct_answer"] = int(q["correct_answer"])
                                        except:
                                            raise ValueError("correct_answer must be an integer")
                                
                                st.session_state.quiz_generated = True
                                st.session_state.current_question = 0
                                st.session_state.score = 0
                                st.session_state.quiz_completed = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error parsing quiz questions: {str(e)}")
                                st.write("Raw response:")
                                st.code(response_content)
                        except Exception as e:
                            st.error(f"Error generating quiz: {str(e)}")
            
            # Display quiz questions
            if st.session_state.quiz_generated and not st.session_state.quiz_completed:
                # Create a progress bar
                progress = st.progress((st.session_state.current_question) / len(st.session_state.quiz_questions))
                
                # Get current question
                question_data = st.session_state.quiz_questions[st.session_state.current_question]
                
                # Display question
                st.markdown(f"### Question {st.session_state.current_question + 1} of {len(st.session_state.quiz_questions)}")
                st.markdown(f"**{question_data['question']}**")
                
                # Display options and get user answer
                selected_option = st.radio(
                    "Select your answer:",
                    question_data['options'],
                    key=f"q{st.session_state.current_question}"
                )
                
                # Get the index of the selected option
                selected_index = question_data['options'].index(selected_option)
                
                # Submit button
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Submit Answer", key="submit_answer", use_container_width=True):
                        # Check if answer is correct
                        if selected_index == question_data['correct_answer']:
                            st.success("✅ Correct!")
                            st.session_state.score += 1
                        else:
                            correct_option = question_data['options'][question_data['correct_answer']]
                            st.error(f"❌ Incorrect. The correct answer is: {correct_option}")
                        
                        # Move to next question or end quiz
                        if st.session_state.current_question < len(st.session_state.quiz_questions) - 1:
                            st.session_state.current_question += 1
                            st.rerun()
                        else:
                            st.session_state.quiz_completed = True
                            st.rerun()
                
                with col2:
                    if st.button("Skip Question", key="skip_question", use_container_width=True):
                        if st.session_state.current_question < len(st.session_state.quiz_questions) - 1:
                            st.session_state.current_question += 1
                        else:
                            st.session_state.quiz_completed = True
                        st.rerun()
            
            # Display quiz results
            if st.session_state.quiz_completed:
                st.markdown("## Quiz Results")
                st.markdown(f"### Your Score: {st.session_state.score}/{len(st.session_state.quiz_questions)}")
                
                # Calculate percentage
                percentage = (st.session_state.score / len(st.session_state.quiz_questions)) * 100
                
                # Display different messages based on score
                if percentage >= 80:
                    st.success(f"🎉 Excellent! You scored {percentage:.1f}%")
                elif percentage >= 60:
                    st.info(f"👍 Good job! You scored {percentage:.1f}%")
                else:
                    st.warning(f"📚 Keep studying! You scored {percentage:.1f}%")
                
                # Button to restart quiz
                if st.button("Take Another Quiz", key="restart_quiz", use_container_width=True, type="primary"):
                    st.session_state.quiz_generated = False
                    st.session_state.quiz_questions = []
                    st.session_state.current_question = 0
                    st.session_state.score = 0
                    st.session_state.quiz_completed = False
                    st.rerun()
    
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
