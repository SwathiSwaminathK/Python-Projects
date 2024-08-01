import tkinter as tk
import threading
import pyaudio
import wave
import os
import whisper_prompt
from langchain.chains import LLMChain
from openai import OpenAI
from pydub import AudioSegment
from tkinter import scrolledtext
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
client = OpenAI()
OpenAI.api_key = os.environ['OPENAI_API_KEY']
global text
text =""
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

from langchain.schema.language_model import BaseLanguageModel
from openai import OpenAI

class OpenAIWrapper(BaseLanguageModel):
    def __init__(self):
        self.llm = OpenAI()

    def generate(self, prompts, **kwargs):
        pass

class ChatWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Chatbot")
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(self.master, width=70, height=20)
        self.chat_display.pack(padx=10, pady=10)

        # User input
        self.user_input = tk.Entry(self.master, width=70)
        self.user_input.pack(padx=10, pady=10)

        self.microphone_button = tk.Button(self.master, text="Start Recording", command=self.toggle_recording)
        self.microphone_button.pack(padx=10, pady=10)

        # Send button
        self.send_button = tk.Button(self.master, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=10)
        
        self.recording = False
        self.frames = []
        
    def send_message(self):
        from openai import OpenAI
        client = OpenAI()
        self.message = self.user_input.get()
        if self.message.strip() != "":
            self.chat_display.insert(tk.END, "You: " + self.message + "\n\n")
            user_msg = self.message
            messages = [{"role": "user", "content": user_msg}]
            '''response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a helpful assistant, who gives response for user in standard english format. If you don't understand user's question then say 'I don't understand.'  """},
                    {"role": "user", "content": user_msg}
                ]
            )
            self.chat_display.insert(tk.END, "Bot: " + response.choices[0].message.content + "\n")'''
            
            
            '''response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                temperature=0,
            )
            self.chat_display.insert(tk.END, "Bot: " + response.choices[0].text + "\n\n")'''
            
            # Add your logic to generate bot response here
            self.chat_display.insert(tk.END, "Bot: Hello, How can I help you?" + "\n\n")
            self.user_input.delete(0, tk.END)  
    
    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.microphone_button.config(text="Stop Recording")
            self.record_audio()
        else:
            self.recording = False
            self.microphone_button.config(text="Start Recording")
            self.save_audio()
            self.audio_to_text()

    def record_audio(self):
        self.frames = []
        self.audio_thread = threading.Thread(target=self._record_audio)
        self.audio_thread.start()

    def _record_audio(self):
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

        while self.recording:
            data = stream.read(CHUNK)
            self.frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def save_audio(self):
        if self.frames:
            wf = wave.open("recorded_audio.wav", 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))
            wf.close()

    def audio_to_text(self):
        files = []
        text = ""
        audio_file_path = "recorded_audio.wav"
        audio_extension = audio_file_path.split('.')[-1]
        audio_file = AudioSegment.from_wav(audio_file_path)
        output_prefix = "minutes_"
        one_second = 1000
        one_minute = 60 * 1000
        total_duration_seconds = round(audio_file.duration_seconds + 1)
        total_duration_seconds_milliseconds = total_duration_seconds * 1000
        chunk_unit =  one_minute
        for index, audio_segment in enumerate(range(0, total_duration_seconds_milliseconds, chunk_unit)):
            audio_file[audio_segment:audio_segment+one_minute].export( output_prefix + str(index + 1) + '.' + audio_extension, format=audio_extension) 
            files.append(output_prefix + str(index + 1) + '.' + audio_extension)
        from openai import OpenAI
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
                language = "en"
            )
            text += response.text
            media_file.close()
        for i in files:
            file_name = i
            file_path = os.path.join(cwd, file_name)
            os.remove(file_path)
        from langchain_openai import OpenAI    
        chat = OpenAI()
        memory = ConversationBufferMemory(memory_key="chat_history", input_key="input")
        prompt = whisper_prompt.prompt
        chain = LLMChain(llm=chat, prompt=prompt,memory=memory)
        response = chain({'input':text})
        answer_text = response['text']

        self.user_input.insert(tk.END, answer_text)
     

def main():
    root = tk.Tk()
    #chat_window = ChatWindow(root)
    ChatWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()