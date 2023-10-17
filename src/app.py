from flask import Flask, send_from_directory, jsonify
import json
import os

app = Flask(__name__, static_url_path='')

rootPath = os.getcwd() + '/src'

print(rootPath)

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

@app.route('/getCampaigns', methods=['GET'])
def get_campaigns():
    campaigns = os.listdir(rootPath + '/notes')
    return jsonify(campaigns)

@app.route('/getSessions/<string:campaign>', methods=['GET'])
def get_sessions(campaign):
    sessions = [f.replace('notes-', '').replace('transcript-', '').replace('.txt', '')
                for f in os.listdir(f'{rootPath}/notes/{campaign}')
                if f.startswith('note-') or f.startswith('transcript-')]
    
    # Convert the list to a set to remove duplicates, then convert back to a list
    sessions_set = set(sessions)
    
    # Since you know each session will have two files, you can ensure that the list only
    # contains unique sessions by only taking half the length of the set
    unique_sessions = list(sessions_set)[:len(sessions_set)//2]
    
    unique_sessions = sorted(unique_sessions)
    return jsonify(unique_sessions)

@app.route('/getTranscriptLine/<string:selectedCampaign>/<string:selectedSession>/<int:line_number>', methods=['GET'])
def get_transcript_line(selectedCampaign, selectedSession, line_number):
    transcript = load_transcript(selectedCampaign, selectedSession)
    if line_number > 0 and line_number <= len(transcript):
        return jsonify(transcript[line_number - 1])
    else:
        return ''

@app.route('/getTranscript/<string:selectedCampaign>/<string:selectedSession>', methods=['GET'])
def get_transcript(selectedCampaign, selectedSession):
    transcript = load_transcript(selectedCampaign, selectedSession)
    return jsonify(transcript)

@app.route('/getNotes/<string:selectedCampaign>/<string:selectedSession>')
def get_notes(selectedCampaign, selectedSession):
    file_path = rootPath + "/notes/" + selectedCampaign + "/note-" + selectedSession + ".txt"
    with open(file_path, 'r') as f:
        notes = json.load(f)
    return jsonify(notes)

def load_transcript(selectedCampaign, selectedSession):
    transcript = []
    file_path = rootPath + "/notes/" + selectedCampaign + "/transcript-" + selectedSession + ".txt"
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line_number, speaker_content = line.split(' ', 1)
            speaker_content_parts = speaker_content.split(': ', 1)
            if len(speaker_content_parts) == 2:
                speaker, content = speaker_content_parts
            else:  # Handle lines without ": "
                speaker = speaker_content_parts[0]
                content = ""
            transcript.append({
                'number': int(line_number[1:-1]),  # remove brackets
                'speaker': speaker,
                'content': content.strip()
            })
    return transcript

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=40515)

