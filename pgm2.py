import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
OpenAI.api_key = os.environ['OPENAI_API_KEY']
client = OpenAI()
with open("dental2.mp3", "rb") as media_file:
    response = client.audio.transcriptions.create(
    model="whisper-1",
    file=media_file,
    language="en"
)
print(response.text)