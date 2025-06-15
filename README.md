---
title: Ai_Doctor
app_file: gradio_app.py
sdk: gradio
sdk_version: 5.32.0
---
# 🩺 AI Doctor with Voice and Vision

An AI-powered healthcare assistant that analyzes medical images and voice inputs to provide preliminary insights. Built with Gradio, Groq, and gTTS.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![AI Doctor Demo](demo-banner.gif) <!-- Add your demo GIF/video link here -->

## ✨ Features

- 🎤 Voice input through microphone
- 🖼️ Medical image analysis capability
- 💬 AI-generated diagnostic suggestions
- 🗣️ Text-to-speech response system
- 🚀 Gradio-powered web interface

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/Subhashbisnoi/ai-doctor-voice-and-vision.git
cd ai-doctor-voice-and-vision
```
## Install dependencies:
```
pip install -r requirements.txt
```
## Create .env file:
```
GROQ_API_KEY=your_api_key_here
```
## 🔧 Configuration

1.Get your Groq API key
2.Add it to .env file
3.For audio recording, ensure PortAudio is installed:
```
# Ubuntu/Debian
sudo apt-get install portaudio19-dev

# macOS
brew install portaudio
```
## 🚀 Usage

Run the application:
```
python gradio_app.py
```
##Access via:

Local URL: http://localhost:7860
Network URL: http://your-ip-address:7860
## 🧩 Project Structure
```
.
├── gradio_app.py          # Main application interface
├── brain_of_the_doctor.py # Image analysis and AI processing
├── voice_of_the_patient.py# Speech recognition module
├── voice_of_the_doctor.py # Text-to-speech functionality
├── requirements.txt       # Dependency list
└── .env.example           # Environment template
```
## 🤝 Contributing

We welcome contributions! Please follow these steps:

- Fork the repository
- Create your feature branch (git checkout -b feature/amazing-feature)
- Commit your changes (git commit -m 'Add some amazing feature')
- Push to the branch (git push origin feature/amazing-feature)
- Open a Pull Request
## ⚠️ Disclaimer

This is a proof-of-concept project and should not be used for actual medical diagnosis. Always consult a qualified healthcare professional for medical advice.

## 🙏 Acknowledgments

- Groq for powerful AI inference
- Gradio for intuitive UI components
- Google Text-to-Speech for voice synthesis
- SpeechRecognition library for audio processing







