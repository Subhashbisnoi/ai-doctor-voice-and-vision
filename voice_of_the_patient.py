# voice_of_the_patient.py (Updated with better retry handling)
from dotenv import load_dotenv

load_dotenv()

import logging
from groq import Groq
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def transcribe_with_groq(stt_model, audio_filepath, GROQ_API_KEY, language="en", max_retries=3):
    client = Groq(api_key=GROQ_API_KEY)

    for attempt in range(max_retries):
        try:
            with open(audio_filepath, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model=stt_model,
                    file=audio_file,
                    language=language
                )
            return transcription.text
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logging.warning(f"Transcription attempt {attempt + 1} failed. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logging.error(f"Transcription failed after {max_retries} attempts: {e}")
                return "Could not transcribe audio. Please try again."