# brain_of_the_doctor.py
from dotenv import load_dotenv

load_dotenv()

import os
import base64
from groq import Groq
import time


def encode_image(image_path):
    """Encode image to base64"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Image encoding error: {e}")
        return None


def analyze_image_with_query(query, model, encoded_image, max_retries=3):
    """Analyze image with Groq API"""
    if not encoded_image:
        return "Could not process the image. Please try another one."

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                },
            ],
        }
    ]

    for attempt in range(max_retries):
        try:
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=model
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Image analysis attempt {attempt + 1} failed. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Image analysis failed after {max_retries} attempts: {e}")
                return "I'm having trouble analyzing this image. Please try again."


def translate_text(text, source_lang, target_lang, GROQ_API_KEY):
    """Translate text between languages"""
    if not text.strip():
        return ""

    client = Groq(api_key=GROQ_API_KEY)
    lang_map = {"English": "en", "Hindi": "hi", "en": "en", "hi": "hi"}

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a professional medical translator. "
                        f"Translate this text from {source_lang} to {target_lang} "
                        "without adding any explanations. Maintain medical terminology accuracy."
                    )
                },
                {"role": "user", "content": text}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text on failure