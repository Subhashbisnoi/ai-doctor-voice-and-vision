# voice_of_the_doctor.py (Updated)
from dotenv import load_dotenv
load_dotenv()

import os
from gtts import gTTS

def text_to_speech_with_gtts(input_text, output_filepath, language="en"):
    if not input_text.strip():
        return ""
        
    try:
        audioobj = gTTS(
            text=input_text,
            lang=language,
            slow=False
        )
        audioobj.save(output_filepath)
        return output_filepath
    except Exception as e:
        print(f"TTS error: {e}")
        return ""