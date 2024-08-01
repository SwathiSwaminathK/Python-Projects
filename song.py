import os
from openai import OpenAI
import sounddevice
from scipy.io.wavfile import write
from pydub import AudioSegment
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
OpenAI.api_key = os.environ['OPENAI_API_KEY']
files = []
text = ""
fs= 44100
second =  int(input("Enter time duration in seconds: "))
print("Recording.....")
record_voice = sounddevice.rec( int ( second * fs ) , samplerate = fs , channels = 2 )
sounddevice.wait()
write("out1.wav",fs,record_voice)
print("Finished Recording.....")
print("Loading Transcription...")
audio_file_path = "out1.wav"
#audio_file_path = "Greatest_Speech_by_Steve_Jobs_.mp3"
audio_extension = audio_file_path.split('.')[-1]
audio_file = AudioSegment.from_wav(audio_file_path)
#audio_file = AudioSegment.from_mp3(audio_file_path)
output_prefix = "minutes_"
one_second = 1000
one_minute = 60 * 1000
ten_minutes = one_minute * 10

total_duration_seconds = round(audio_file.duration_seconds + 1)
total_duration_seconds_milliseconds = total_duration_seconds * 1000

chunk_unit =  one_minute
for index, audio_segment in enumerate(range(0, total_duration_seconds_milliseconds, chunk_unit)):
    audio_file[audio_segment:audio_segment+one_minute].export( output_prefix + str(index + 1) + '.' + audio_extension, format=audio_extension) 
    files.append(output_prefix + str(index + 1) + '.' + audio_extension)
client = OpenAI()
model_id = "whisper-1"
cwd = os.getcwd()
for i in files:
    file_name = i
    file_path = os.path.join(cwd, i)
    media_file = open(file_path,"rb")

    response = client.audio.transcriptions.create(
        model = model_id,
        file = media_file,
    )
    text += response.text
    #print(response.text)
    media_file.close()
print(text)    
for i in files:
    file_name = i
    file_path = os.path.join(cwd, i)
    os.remove(file_path)
    
'''client = OpenAI()
model_id = "whisper-1"
cwd = os.getcwd()
file_name = "out.wav"
file_path = os.path.join(cwd, file_name)
media_file = open(file_path,"rb")

response = client.audio.transcriptions.create(
    model = model_id,
    file = media_file,
)
print(response.text)'''
