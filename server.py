from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO
import requests

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        password = request.form.get('password')
        return redirect(url_for('chat', api_key=api_key, password=password))
    return render_template('login.html')

@app.route('/chat')
def chat():
    api_key = request.args.get('api_key')
    password = request.args.get('password')
    return render_template('chat.html', api_key=api_key, password=password)

@socketio.on('send_message')
def handle_message(message):
    api_key = message['apiKey']
    user_input = message['userInput']

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    payload = {
        "prompt": user_input,
        "max_tokens": 100
    }

    try:
        response = requests.post('https://api.openai.com/v1/engines/davinci-codex/completions', headers=headers, json=payload)
        bot_response = response.json()['choices'][0]['text'].strip()
        socketio.emit('new_message', {'user': 'Bot', 'message': bot_response})

        # Storing chat logs
        with open('chat_logs.txt', 'a') as f:
            f.write(f"User: {user_input}\n")
            f.write(f"Bot: {bot_response}\n")

    except Exception as e:
        print(e)

if __name__ == '__main__':
    socketio.run(app, debug=True)
