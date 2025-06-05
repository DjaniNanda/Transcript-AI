# Transcript AI 🎧🧠

**Transcript AI** is a simple and intuitive desktop application that transcribes audio files into text using OpenAI's Whisper model. It's designed for users who prefer a graphical interface over command-line tools.

## Features

- 🎙️ Transcribe audio files (MP3, WAV, etc.) with a click
- 🧠 Powered by OpenAI's Whisper ASR model
- 🖥️ Clean and user-friendly GUI (built with `tkinter`)
- 🌍 Multilingual support
- 💾 Saves transcript to a `.txt` file

## Installation

### Requirements

- Python 3.8+
- `ffmpeg` (required by Whisper)
- Dependencies listed in `requirements.txt`

### Steps

1. Clone the repository:

        git clone https://github.com/DjaniNanda/Transcript-AI.git
        cd Transcript-AI 

2. Create and activate a virtual environment (optional but recommended):
 
        python -m venv venv
        # On macOS/Linux
        source venv/bin/activate
        # On Windows
        venv\Scripts\activate
  
3. Install the dependencies:
 
       pip install -r requirements.txt
   
   If there is no requirements.txt, create one with:
   
        openai-whisper
        torch
        tk


5. Make sure ffmpeg is installed and available in your system path:

  - Windows: Download from ffmpeg.org and add to PATH
  
  - macOS: brew install ffmpeg
  
  - Linux: sudo apt install ffmpeg

## Usage
Run the application with:

    python whisper_transcriber.py  
    
## How It Works
  1. Launch the app
     
  2. Click "Browse" to select an audio file
     
  3. Click "Transcribe"
     
  4. Transcript will appear in the window and be saved as a .txt file
     
## License
This project is licensed under the MIT License. See the LICENSE file for details.
