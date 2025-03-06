# SpeechNotes AI

![SpeechNotes AI Logo](https://img.shields.io/badge/SpeechNotes-AI-blue?style=for-the-badge)

A powerful speech-to-text application that transcribes audio files and generates
concise bullet point summaries using AI.

## 🌟 Features

- **Audio Transcription**: Convert speech from audio files to text using
  Deepgram's advanced AI
- **Bullet Point Summaries**: Generate concise, well-organized bullet point
  summaries from transcriptions using Groq's LLaMA 3.3 model
- **Tabbed Interface**: Toggle between transcription and summary views
- **Download Options**: Save both transcriptions and summaries as text files
- **Multiple Audio Formats**: Support for MP3, WAV, and OGG audio files

## 📋 Requirements

- Python 3.8+
- Streamlit
- Deepgram API Key (for transcription)
- Groq API Key (for summarization)

## 🚀 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/speechnotes-ai.git
   cd speechnotes-ai
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## 🔑 API Keys

This application requires two API keys:

1. **Deepgram API Key**: For transcribing audio to text

   - Sign up at [console.deepgram.com](https://console.deepgram.com)
   - Create a new API key in your account

2. **Groq API Key**: For generating bullet point summaries
   - Sign up at [console.groq.com](https://console.groq.com)
   - Create a new API key in your account

You'll enter these keys in the application's sidebar when running the app.

## 🖥️ Usage

1. Start the application:

   ```bash
   streamlit run main.py
   ```

2. Enter your Deepgram and Groq API keys in the sidebar

3. Upload an audio file (MP3, WAV, or OGG format)

4. Click "Transcribe Audio" to generate the transcription

5. Click "Generate Notes" to create a bullet point summary

6. Toggle between the transcription and summary using the tabs

7. Download the transcription or summary as a text file

## 📸 Screenshots

_[Add screenshots of your application here]_

## 🛠️ Technologies Used

- **Streamlit**: For the web application interface
- **Deepgram API**: For high-quality speech-to-text transcription
- **Groq API**: For generating AI-powered bullet point summaries
- **LLaMA 3.3 70B Model**: For creating concise, well-organized summaries

## 📝 How It Works

1. **Audio Upload**: User uploads an audio file through the Streamlit interface
2. **Transcription**: Deepgram's AI transcribes the audio to text
3. **Summarization**: Groq's LLaMA 3.3 model processes the transcription to
   create bullet point summaries
4. **Display**: Results are displayed in a tabbed interface for easy viewing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for
details.

##  Acknowledgements

- [Deepgram](https://deepgram.com) for their speech-to-text API
- [Groq](https://groq.com) for their fast LLM inference API
- [Streamlit](https://streamlit.io) for the web application framework

