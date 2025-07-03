import os
import time
import pyttsx3
import speech_recognition as sr
import requests
import json

# ✅ Use Ollama's free local model (e.g., mistral)
# def get_local_reply(prompt):
#     try:
#         response = requests.post(
#             "http://localhost:11434/api/chat",
#             json={
#                 "model": "mistral",
#                 "messages": [{"role": "user", "content": prompt}]
#             }
#         )

#         # ✅ Print raw response for debugging
#         print("🔍 Raw Ollama Response:\n", response.text)

#         # Parse response safely
#         response_lines = response.text.strip().splitlines()

#         # Find the last valid message
#         for line in reversed(response_lines):
#             try:
#                 data = json.loads(line)
#                 if "message" in data and "content" in data["message"]:
#                     return data["message"]["content"]
#             except (json.JSONDecodeError, KeyError):
#                 continue

#         print("⚠️ No message.content found in any response lines.")
#         return "I'm sorry, I couldn't find an answer."
#     except Exception as e:
#         return f"❌ Error using local model: {e}"

def get_local_reply(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "mistral",
                "messages": [{"role": "user", "content": prompt}],
                "stream": True
            },
            stream=True  # ✅ Important to enable response streaming
        )

        full_reply = ""

        # ✅ Read streamed chunks line by line
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if "message" in data and "content" in data["message"]:
                        full_reply += data["message"]["content"]
                except json.JSONDecodeError:
                    continue

        return full_reply.strip() or "⚠️ I couldn't generate a full response."
    except Exception as e:
        return f"❌ Error using local model: {e}"

# ✅ Initialize text-to-speech engine with Samantha voice
def init_tts():
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')

        samantha_voice = next((v for v in voices if 'Samantha' in v.name), None)
        if samantha_voice:
            engine.setProperty('voice', samantha_voice.id)
            print("✅ Voice set to Samantha")
        else:
            print("⚠️ 'Samantha' voice not found. Using default.")
        return engine
    except Exception as e:
        print(f"❌ TTS Init Error: {e}")
        return None

# ✅ Speak using pyttsx3
def speak(text, engine):
    if engine:
        engine.say(text)
        engine.runAndWait()
    else:
        print("🗣️ (Text):", text)

# ✅ Take voice input using microphone
def take_command():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🎤 Listening... (speak now)")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        print("🧠 Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"✅ You said: {query}")
        return query
    except sr.WaitTimeoutError:
        print("⏱️ Timed out waiting for speech.")
    except sr.UnknownValueError:
        print("❓ Could not understand.")
    except sr.RequestError as e:
        print(f"🌐 Speech Recognition error: {e}")
    except Exception as e:
        print(f"⚠️ Mic error: {e}")
    return None

# ✅ Main
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
            reply = get_local_reply(query)
            print("🤖 GPT:", reply)
            speak(reply, tts_engine)
        else:
            speak("Please say that again.", tts_engine)