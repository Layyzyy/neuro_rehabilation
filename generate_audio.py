from gtts import gTTS
from pydub import AudioSegment
import simpleaudio as sa

def make(file, text):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(file.replace(".wav", ".mp3"))
    audio = AudioSegment.from_mp3(file.replace(".wav", ".mp3"))
    audio.export(file, format="wav")
    print(f"Generated: {file}")

sounds = {
    "press.wav": "Press now",
    "getready.wav": "Get ready",
    "hold3sec.wav": "Hold for three seconds",
    "3.wav": "Three",
    "2.wav": "Two",
    "1.wav": "One",
    "release.wav": "Release slowly",
    "goodjob.wav": "Good job, next repetition",
    "ding.wav": "ding"
}

for file, text in sounds.items():
    make(file, text)

print("All audio files generated successfully!")
