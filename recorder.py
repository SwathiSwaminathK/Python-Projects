import os
import pymysql
import threading
import pyaudio
import wave
import whisper_prompt
from pydub import AudioSegment
import concurrent.futures
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from prompt import Prompt

db4 = pymysql.connect(host='localhost', user='root', password='Srsweb@123#', database='Openai_whisper')

class ChatWindow:
    def __init__(self):
        self.recording = False
        self.frames = []
        self.audio_thread = None
        
    def send_message(self):
        from openai import OpenAI
        client = OpenAI()
        self.message = "self"
        if self.message.strip() != "":
            pass
    
    def toggle_recording(self, start_recording):
        if start_recording:
            if not self.recording:
                print("Started Recording")
                self.recording = True
                self.record_audio()
                return "Recording started"
        else:
            if self.recording:
                print("Stopped Recording")
                self.recording = False
                if self.audio_thread:
                    self.audio_thread.join()
                self.save_audio()
                converted_text = self.audio_to_text()
                return converted_text

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
        try:
            files = []
            speech_text = ""
            audio_file_path = "recorded_audio.wav"
            audio_extension = audio_file_path.split('.')[-1]
            audio_file = AudioSegment.from_wav(audio_file_path)
            output_prefix = "minutes_"
            one_second = 1000
            one_minute = 60 * 1000
            total_duration_seconds = round(audio_file.duration_seconds + 1)
            total_duration_seconds_milliseconds = total_duration_seconds * 1000
            chunk_unit = one_minute

            def process_audio_chunk(audio_segment, index):
                from openai import OpenAI
                client = OpenAI()
                segment_duration = min(one_minute, total_duration_seconds_milliseconds - audio_segment)
                if segment_duration > 100:
                    chunk_audio_path = f"{output_prefix}{index + 1}.{audio_extension}"
                    audio_file[audio_segment:audio_segment + one_minute].export(chunk_audio_path, format=audio_extension)
                    files.append(chunk_audio_path)
                    with open(chunk_audio_path, "rb") as media_file:
                        response = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=media_file,
                            language="en"
                        )
                        return response.text

            with concurrent.futures.ThreadPoolExecutor() as executor:
                chunk_indices = range(0, total_duration_seconds_milliseconds, chunk_unit)
                results = executor.map(process_audio_chunk, chunk_indices, range(len(chunk_indices)))
                for result in results:
                    if result:
                        speech_text += result
            
            for file_path in files:
                os.remove(file_path)
            os.remove("recorded_audio.wav")
            return speech_text
            ''' from openai import OpenAI
            client = OpenAI()
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": Prompt},
                    {"role": "user", "content": speech_text}
                ]
            )
            converted_text = response.choices[0].message.content # str(converted_text)
            patient_start_index = converted_text.find('Patient: ') + len('Patient: ')
            patient_end_index = converted_text.find('\n', patient_start_index)
            patient_name = converted_text[patient_start_index:patient_end_index].strip()
            
            insert_query = """
                        INSERT INTO trial_whisper (patient_name, report_text)
                        VALUES (%(patient_name)s, %(report_text)s)
                        """
            data_to_insert = {
                            'patient_name': patient_name,
                            'report_text': response.choices[0].message.content,
                        }
            cursor4 = db4.cursor()
            cursor4.execute(insert_query, data_to_insert)
            db4.commit()
            cursor4.close()
            return response.choices[0].message.content '''
        except Exception as e:
            print(e)
