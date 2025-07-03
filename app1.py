import os
import time
import pyttsx3
import speech_recognition as sr
# from openai import OpenAI
from apikey import api_data
import requests

def get_local_reply(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",  # Ollama default server
            json={
                "model": "mistral",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        return response.json()['message']['content']
    except Exception as e:
        return f"Error using local model: {e}"
# Initialize OpenAI client
# client = OpenAI(api_key=api_data)

# Initialize text-to-speech engine (cross-platform)
def init_tts():
    try:
        engine = pyttsx3.init()  # Automatically picks driver: sapi5 (Windows), nsss (macOS), espeak (Linux)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)  # Change index if needed
        return engine
    except Exception as e:
        print(f"Text-to-speech engine initialization failed: {e}")
        return None

# Speak text aloud
def speak(text, engine):
    if engine:
        engine.say(text)
        engine.runAndWait()
    else:
        print("Speaking disabled. (TTS engine not available)")

def take_command():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🎤 Listening... (speak now)")
            recognizer.pause_threshold = 1
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        print("🧠 Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"✅ You said: {query}")
        return query

    except sr.WaitTimeoutError:
        print("⏱️ Listening timed out while waiting for phrase.")
    except sr.UnknownValueError:
        print("❓ Could not understand the audio.")
    except sr.RequestError as e:
        print(f"🌐 Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        print(f"⚠️ Microphone or recognition error: {e}")

    return None

# Initialize text-to-speech engine (cross-platform)
def init_tts():
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')

        # Try to find 'Samantha' voice
        samantha_voice = next((voice for voice in voices if 'Samantha' in voice.name), None)
        
        if samantha_voice:
            engine.setProperty('voice', samantha_voice.id)
            print("✅ Voice set to Samantha")
        else:
            print("⚠️ 'Samantha' voice not found. Using default voice.")

        return engine
    except Exception as e:
        print(f"Text-to-speech engine initialization failed: {e}")
        return None

# Get response from OpenAI
def get_gpt_reply(prompt):
    try:
        response = get_local_reply.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "Sorry, I couldn't get a response from OpenAI."

if __name__ == "__main__":
    tts_engine = init_tts()
    speak("Hello! How can I assist you today?", tts_engine)

    while True:
        query = take_command()
        if query:
            query = query.lower()
            if 'exit' in query or 'quit' in query:
                speak("Goodbye!", tts_engine)
                break
            reply = get_gpt_reply(query)
            print("GPT:", reply)
            speak(reply, tts_engine)
        else:
            speak("Please say that again.", tts_engine)
            break