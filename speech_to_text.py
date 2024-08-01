import os
import pyaudio
import wave
import openai
from openai import OpenAI
import sounddevice
from scipy.io.wavfile import write
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
OpenAI.api_key = os.environ['OPENAI_API_KEY']
client = OpenAI()

print("Recording.....")
recording = False
frames = []
audio_thread = None
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 10

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

while recording:
    data = stream.read(CHUNK)
    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()
if frames:
    wf = wave.open("recorded_audio.wav", 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()
print("Finished Recording.....")
print("Loading Transcription...")
model_id = "whisper-1"
cwd = os.getcwd()
file_name = "recorded_audio.wav"
file_path = os.path.join(cwd, file_name)
media_file = open(file_path,"rb")
response = client.audio.transcriptions.create(
    model = model_id,
    file = media_file,
)
print(response.text)