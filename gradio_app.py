# gradio_app.py
from dotenv import load_dotenv

load_dotenv()

import os
import gradio as gr
import uuid
import datetime
import sqlite3
from database import create_user, authenticate_user, save_consultation, get_user_history
from brain_of_the_doctor import encode_image, analyze_image_with_query, translate_text
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts

# Optimized system prompt
system_prompt = """
As a medical professional examining this image, provide your analysis directly to the patient.
If you observe any medical concerns:
1. Clearly describe your findings in plain language
2. Suggest potential next steps or remedies
3. Keep your response to 1-2 concise sentences

Structure your response as if speaking directly to the patient:
"Based on what I'm seeing, [your observation]. I recommend [suggestion]."

Important:
- Avoid AI/model references
- Skip technical disclaimers
- Never use markdown formatting
- Start immediately with your analysis
"""

# State management
current_user = gr.State(None)


def process_inputs(audio_filepath, image_filepath, language, user_state):
    """Process user inputs and generate medical analysis"""
    if not user_state:
        return "Please log in first", "", ""

    lang_code = "hi" if language == "Hindi" else "en"

    # Generate unique filenames
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    audio_response_path = f"response_{user_state['user_id']}_{timestamp}.mp3"

    # Initialize variables
    patient_speech = ""
    doctor_response = ""
    display_doctor_response = ""

    try:
        # Transcribe patient's speech
        patient_speech = transcribe_with_groq(
            stt_model="whisper-large-v3",
            audio_filepath=audio_filepath,
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
            language=lang_code
        )
    except Exception as e:
        patient_speech = f"Speech recognition error: {str(e)}"

    display_patient_speech = patient_speech

    # Translate if needed
    if language == "Hindi":
        patient_query = translate_text(
            text=patient_speech,
            source_lang="hi",
            target_lang="en",
            GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
        )
    else:
        patient_query = patient_speech

    # Image analysis
    encoded_img = encode_image(image_filepath) if image_filepath else None

    if encoded_img:
        doctor_response = analyze_image_with_query(
            query=f"{system_prompt}\n\nPatient says: {patient_query}",
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            encoded_image=encoded_img
        )
    else:
        doctor_response = "Please provide an image for analysis"

    # Translate response
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
    text_to_speech_with_gtts(
        input_text=display_doctor_response,
        output_filepath=audio_response_path,
        language=tts_lang
    )

    # Save to database
    save_consultation(
        user_id=user_state["user_id"],
        audio_path=audio_filepath,
        image_path=image_filepath,
        patient_speech=patient_speech,
        doctor_response=doctor_response,
        audio_response_path=audio_response_path,
        language=language
    )

    return display_patient_speech, display_doctor_response, audio_response_path


def login_user(username, password):
    """Authenticate user and return state"""
    user = authenticate_user(username, password)
    if user:
        return {**user, "username": username}, f"Welcome, {user['full_name']}!"
    return None, "Invalid username or password"


def create_account(username, password, full_name):
    """Create a new user account"""
    if create_user(username, password, full_name):
        return login_user(username, password)
    return None, "Username already exists"


# Function to render history UI content as a single HTML string
def render_history_ui_content(user_state):
    """Dynamically creates and returns a single HTML string for the history section."""
    if not user_state:
        # If no user, hide the container and return empty HTML
        return gr.update(visible=False), ""

    history = get_user_history(user_state["user_id"])

    html_content = ""

    if not history:
        html_content = "<p>No consultation history found.</p>"
    else:
        html_content = f"<h2>Medical History for {user_state['full_name']}</h2>"
        for consult in history:
            html_content += f"""
            <details style="border: 1px solid #ccc; border-radius: 5px; margin-bottom: 10px; padding: 10px; background-color: var(--background-fill-secondary);">
                <summary style="font-weight: bold; cursor: pointer; padding: 5px; background-color: var(--block-background);">
                    Consultation - {consult['timestamp']} ({consult['language']})
                </summary>
                <div style="padding: 10px;">
                    <p><strong>Date:</strong> {consult['timestamp']}</p>
                    <p><strong>Language:</strong> {consult['language']}</p>
                    <h3>Patient's Description</h3>
                    <p>{consult['patient_speech']}</p>
                    <h3>Doctor's Analysis</h3>
                    <p>{consult['doctor_response']}</p>
            """
            # Note: Embedding local audio/image files directly in gr.HTML for playback/display
            # requires base64 encoding or a Gradio server route for static files,
            # which adds complexity. For now, we'll just indicate their presence.
            if consult.get('audio_path'):
                html_content += f"<p>Patient's Audio: Available (File: {os.path.basename(consult['audio_path'])})</p>"
            if consult.get('audio_response_path'):
                html_content += f"<p>Doctor's Audio: Available (File: {os.path.basename(consult['audio_response_path'])})</p>"
            if consult.get('image_path'):
                html_content += f"<p>Consultation Image: Available (File: {os.path.basename(consult['image_path'])})</p>"

            html_content += "</div></details>"

    return gr.update(visible=True), html_content


# Custom CSS for clean UI
custom_css = """
.profile-button {
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 14px;
    cursor: pointer;
    margin-left: auto;
    max-width: 120px;
}
.profile-button:hover {
    background-color: #3a7bc8;
}
.history-section {
    margin-top: 20px;
    border-top: 1px solid #e0e0e0;
    padding-top: 20px;
}
.profile-options {
    background-color: var(--background-fill-primary); /* Use Gradio theme variable */
    border: 1px solid var(--border-color-primary); /* Use Gradio theme variable */
    border-radius: 8px;
    padding: 15px;
    margin-top: 10px;
    box-shadow: var(--shadow-drop-lg); /* Use Gradio theme variable */
}
"""

# Main application
with gr.Blocks(title="🩺 AI Doctor with Medical History", theme=gr.themes.Soft(), css=custom_css) as app:
    user_state = gr.State(None)
    login_status = gr.Markdown("", visible=False)

    # Header with profile button
    with gr.Row():
        gr.Markdown("# 🩺 AI Doctor")
        profile_button = gr.Button("Login", elem_classes="profile-button")

    # Authentication section
    with gr.Column(visible=False) as auth_section:
        with gr.Tab("Login"):
            login_username = gr.Textbox(label="Username")
            login_password = gr.Textbox(label="Password", type="password")
            login_btn = gr.Button("Login")

        with gr.Tab("Create Account"):
            create_username = gr.Textbox(label="Choose Username")
            create_password = gr.Textbox(label="Choose Password", type="password")
            create_fullname = gr.Textbox(label="Full Name")
            create_btn = gr.Button("Create Account")

    # Main Content Section
    with gr.Column(visible=False) as main_content:
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Patient Information")
                audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Describe your condition")
                image_input = gr.Image(type="filepath", label="Upload Medical Image")
                language_select = gr.Radio(["English", "Hindi"], label="Language", value="English")
                submit_btn = gr.Button("Analyze Condition")

            with gr.Column():
                gr.Markdown("## Doctor's Analysis")
                patient_speech = gr.Textbox(label="Patient's Speech", interactive=False)
                doctor_response = gr.Textbox(label="Doctor's Analysis", interactive=False)
                doctor_voice = gr.Audio(label="Doctor's Voice Response", interactive=False)

        # History section - this will be the container that gets its visibility updated
        # and its content will be rendered into history_display_html
        with gr.Column(visible=False) as history_section_container:
            history_display_html = gr.HTML("")  # This HTML component will show the history

        # Profile options section (only visible after login)
        with gr.Column(visible=False) as profile_options:
            with gr.Group(elem_classes="profile-options"):
                gr.Markdown("### Profile Options")
                with gr.Row():
                    view_history_btn = gr.Button("View History")
                    logout_btn = gr.Button("Logout")


    # Profile button events
    def toggle_auth_section():
        return gr.Column(visible=True), gr.Column(visible=False)


    profile_button.click(
        toggle_auth_section,
        outputs=[auth_section, main_content]
    )


    # Authentication events
    def update_ui_after_login(user_state_val):
        if user_state_val:
            return [
                gr.Column(visible=False),  # auth_section
                gr.Column(visible=True),  # main_content
                gr.Button("Profile", elem_classes="profile-button"),
                f"Welcome, {user_state_val['full_name']}!",
                gr.Column(visible=True)  # Show profile_options
            ]
        return [
            gr.Column(visible=True),
            gr.Column(visible=False),
            gr.Button("Login", elem_classes="profile-button"),
            "Login failed",
            gr.Column(visible=False)
        ]


    login_btn.click(
        login_user,
        inputs=[login_username, login_password],
        outputs=[user_state, login_status]
    ).then(
        update_ui_after_login,
        inputs=[user_state],
        outputs=[auth_section, main_content, profile_button, login_status, profile_options]
    )

    create_btn.click(
        create_account,
        inputs=[create_username, create_password, create_fullname],
        outputs=[user_state, login_status]
    ).then(
        update_ui_after_login,
        inputs=[user_state],
        outputs=[auth_section, main_content, profile_button, login_status, profile_options]
    )

    # View history button
    view_history_btn.click(
        render_history_ui_content,
        inputs=[user_state],
        outputs=[history_section_container, history_display_html]
    )


    # Logout button
    def logout_user():
        return [
            None,
            gr.Column(visible=False),  # main_content
            gr.Column(visible=True),  # auth_section
            gr.Button("Login", elem_classes="profile-button"),
            "Logged out successfully",
            gr.Column(visible=False),  # profile_options
            gr.update(visible=False),  # Hide history_section_container
            ""  # Clear HTML content of history_display_html
        ]


    logout_btn.click(
        logout_user,
        outputs=[user_state, main_content, auth_section, profile_button, login_status, profile_options,
                 history_section_container, history_display_html]
    )

    # Consultation submission
    submit_btn.click(
        process_inputs,
        inputs=[audio_input, image_input, language_select, user_state],
        outputs=[patient_speech, doctor_response, doctor_voice]
    ).then(
        render_history_ui_content,  # Re-render history after new consultation
        inputs=[user_state],
        outputs=[history_section_container, history_display_html]
    )

# Launch with share=True
app.launch(debug=True, server_port=7710, share=True)