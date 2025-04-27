from flask import Flask, render_template, jsonify
import subprocess
import signal

app = Flask(__name__)

# Global variable to store the subprocess
conversation_process = None

@app.route('/')
def index():
    # Render the index.html template
    return render_template('index.html')

@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    global conversation_process
    # Start the conversation using the existing Eleven Labs code
    conversation_process = subprocess.Popen(['python', 'convai/demo.py'])
    return jsonify({'status': 'started'})

@app.route('/end_conversation', methods=['POST'])
def end_conversation():
    global conversation_process
    if conversation_process:
        # Terminate the subprocess
        conversation_process.terminate()
        conversation_process = None
        return jsonify({'status': 'ended'})
    else:
        return jsonify({'status': 'no active conversation'})

if __name__ == '__main__':
    app.run(debug=True) 