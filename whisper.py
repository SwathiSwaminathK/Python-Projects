from flask import Flask, render_template, jsonify, request
from prompt import Prompt
import os, re
from langchain.chains import LLMChain
from openai import OpenAI
from flask_socketio import SocketIO
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
client = OpenAI()
OpenAI.api_key = os.environ['OPENAI_API_KEY']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey!'
socket = SocketIO(app)

@app.route('/speech_text', methods=['POST'])
def speech_text():
    try:
        text = request.json.get('text')
        if (text == "\n") or (text == ""):
            return jsonify({'text': [], 'status': 'success', "message": 'success'})
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": Prompt},
                {"role": "user", "content": text}
            ]
        )
        answer_text = response.choices[0].message.content
        converted_text = str(answer_text) #str(response)
        print(converted_text)
        '''sections = converted_text.strip().split('\n\n')
        result = []
        order = 1
        for section in sections:
            if section == '':
                continue
            heading, value = section.split(':', 1)
            #value = value.lstrip('\n').strip()
            result.append({'order': order, 'heading': heading, 'value': value})
            order += 1
        #print(result)
        return jsonify({'text': result, 'status': 'success', "message": 'success'})
        #return jsonify({'text': converted_text, 'status': 'success', "message": 'success'})'''
        sections = re.split(r'(?=Subjective:|\n\nObjective:|\n\nAssessment:|\n\nPlan:)', converted_text)
        result = []
        order = 1
        for section in sections:
            if section == '':
                continue
            if section.startswith('Subjective:'):
                heading, value = section.split(':', 1)
                value = value.lstrip('\n')
                result.append({'order': order, 'heading': heading, 'value': value})
                order += 1
        
            elif section.startswith('\n\nObjective:'):
                heading, value = section.split('\n\nObjective:', 1)
                value = value.lstrip('\n')
                result.append({'order': order, 'heading': 'Objective', 'value': value})
                order += 1
        
            elif section.startswith('\n\nAssessment:'):
                heading, value = section.split('\n\nAssessment:', 1)
                value = value.lstrip('\n')
                result.append({'order': order, 'heading': 'Assessment', 'value': value})
                order += 1
        
            elif section.startswith('\n\nPlan:'):
                heading, value = section.split('\n\nPlan:', 1)
                value = value.lstrip('\n')
                result.append({'order': order, 'heading': 'Plan', 'value': value})
                order += 1
        return jsonify({'text': result, 'status': 'success', "message": 'success'})
    except Exception as e:
        result={'status':'failed', "message": e}
        error_message = str(e)
        return jsonify({'status':'failed', "message": error_message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)