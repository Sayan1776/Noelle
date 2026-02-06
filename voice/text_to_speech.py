import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 170)   # slightly softer pace

# Pick a feminine voice
voices = engine.getProperty("voices")
for voice in voices:
    if "zira" in voice.name.lower():
        engine.setProperty("voice", voice.id)
        break


def speak(text: str):
    engine.say(text)
    engine.runAndWait()
