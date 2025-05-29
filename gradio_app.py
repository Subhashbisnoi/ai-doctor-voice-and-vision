from dotenv import load_dotenv
load_dotenv()

#VoiceBot UI with Gradio
import os
import gradio as gr

from brain_of_the_doctor import encode_image, analyze_image_with_query, translate_text
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts




system_prompt="""You have to act as a professional doctor, i know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""


def process_inputs(audio_filepath, image_filepath, language):
    lang_code = "hi" if language == "Hindi" else "en"
    
    # Transcribe patient's speech
    patient_speech = transcribe_with_groq(
        stt_model="whisper-large-v3",
        audio_filepath=audio_filepath,
        GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
        language=lang_code  # Add language parameter
    )
    
    # Display original patient speech
    display_patient_speech = patient_speech
    
    # Translate to English if needed for model processing
    if language == "Hindi":
        patient_query = translate_text(
            text=patient_speech,
            source_lang="hi",
            target_lang="en",
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
        )
    else:
        patient_query = patient_speech

    # Handle image analysis
    if image_filepath:
        doctor_response = analyze_image_with_query(
            query=f"{system_prompt}\n\nPatient says: {patient_query}",
            encoded_image=encode_image(image_filepath),
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        )
    else:
        doctor_response = "Please provide an image for analysis"

    # Translate response back to Hindi if needed
    if language == "Hindi":
        display_doctor_response = translate_text(
            text=doctor_response,
            source_lang="en",
            target_lang="hi",
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
        )
    else:
        display_doctor_response = doctor_response

    # Generate doctor's voice response
    tts_lang = "hi" if language == "Hindi" else "en"
    voice_file = text_to_speech_with_gtts(
        input_text=display_doctor_response,
        output_filepath="final.mp3",
        language=tts_lang
    )

    return display_patient_speech, display_doctor_response, voice_file

iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath"),
        gr.Image(type="filepath"),
        gr.Radio(["English", "Hindi"], label="Patient Language", value="English")
    ],
    outputs=[
        gr.Textbox(label="Patient's Speech"),
        gr.Textbox(label="Doctor's Response"),
        gr.Audio("final.mp3", label="Doctor's Voice")
    ],
    title="Multilingual AI Doctor",
    description="Speak in English or Hindi and get medical analysis"
)

iface.launch(debug=True)