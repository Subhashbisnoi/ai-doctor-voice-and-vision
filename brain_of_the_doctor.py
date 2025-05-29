from dotenv import load_dotenv
load_dotenv()

import os
import base64
from groq import Groq

def encode_image(image_path): 
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_with_query(query, model, encoded_image):
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
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model
    )
    return chat_completion.choices[0].message.content

# New translation function
def translate_text(text, source_lang, target_lang, GROQ_API_KEY):
    client = Groq(api_key=GROQ_API_KEY)
    
    # Language code mapping
    lang_codes = {
        "English": "en",
        "Hindi": "hi",
        "en": "en",
        "hi": "hi"
    }
    
    source = lang_codes.get(source_lang, source_lang)
    target = lang_codes.get(target_lang, target_lang)
    
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"You are a professional medical translator. Translate this text from {source} to {target} without adding any explanations. Maintain medical terminology accuracy."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        max_tokens=1024
    )
    return response.choices[0].message.content