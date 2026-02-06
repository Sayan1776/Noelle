import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

def listen(duration=5, samplerate=16000):
    print("🎤 Listening...")

    audio = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio.append(indata.copy())

    with sd.InputStream(
        samplerate=samplerate,
        channels=1,
        dtype="float32",
        callback=callback
    ):
        sd.sleep(int(duration * 1000))

    audio_np = np.concatenate(audio, axis=0).flatten()

    segments, _ = model.transcribe(audio_np, language="en")
    text = " ".join(segment.text for segment in segments)

    return text.strip()
