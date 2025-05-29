from dotenv import load_dotenv
load_dotenv()

import os
from gtts import gTTS
import subprocess
import platform

def text_to_speech_with_gtts(input_text, output_filepath, language="en"):  # Add language parameter
    audioobj = gTTS(
        text=input_text,
        lang=language,  # Use the language parameter
        slow=False
    )
    audioobj.save(output_filepath)
    os_name = platform.system()
    try:
        if os_name == "Darwin":  # macOS
            subprocess.run(['afplay', output_filepath])
        elif os_name == "Windows":  # Windows
            subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'])
        elif os_name == "Linux":  # Linux
            subprocess.run(['aplay', output_filepath])
        else:
            raise OSError("Unsupported operating system")
    except Exception as e:
        print(f"An error occurred while trying to play the audio: {e}")

# Remove or comment out the test call at the bottom
# input_text="Hi this is subhash from Rajasthan, autoplay"
# text_to_speech_with_gtts(input_text=input_text, output_filepath="gtts_testing.mp3")