from gtts import gTTS
import subprocess

def make(file, text):
    mp3_file = file.replace(".wav", ".mp3")
    wav_file = file
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(mp3_file)
    print(f"Generated: {mp3_file}")
    
    # Convert MP3 to WAV using ffmpeg
    subprocess.run(['ffmpeg', '-i', mp3_file, '-y', wav_file], 
                   capture_output=True, check=True)
    print(f"Converted: {wav_file}")

sounds = {
    "press.wav": "Press now",
    "getready.wav": "Get ready",
    "hold3sec.wav": "Hold for three seconds",
    "3.wav": "Three",
    "2.wav": "Two",
    "1.wav": "One",
    "release.wav": "Release slowly",
    "goodjob.wav": "Good job, next repetition",
    "ding.wav": "done"
}

for file, text in sounds.items():
    make(file, text)

print("All audio files generated successfully!")
