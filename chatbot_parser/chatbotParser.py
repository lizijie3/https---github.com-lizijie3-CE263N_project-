from flask import Flask, request, Response, jsonify
import json
from urllib.parse import urljoin
import requests
import re
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
#456
# python D:\INFO253B\terminal-chat-docker\terminal_chatbot.py http://127.0.0.1:5000

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:postgres@db:5432/chatbot"
db = SQLAlchemy(app)

class Commands(db.Model):
    command = db.Column(db.String(20), primary_key=True)
    server_url = db.Column(db.String(200))

    def to_dict(self):
        return {
            'command': self.command,
            'server_url': self.server_url
        }


# request to specific command server
def make_request_request(server_url, requestToSpecificServer):
    full_url = urljoin(server_url, "/command")
    
    try: 
        r = requests.post(full_url, json=requestToSpecificServer, headers={'Content-type': 'application/json'})
        r.raise_for_status()
    except requests.exceptions.ConnectionError as err:
        raise SystemExit(err)
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    data = r.json() 
    return data

def get_command_url(command):
    command_url = Commands.query.filter_by(command=command).first() 
    if command_url:
        cu = command_url.to_dict()
        return cu['server_url']
    else:
        return 0

@app.route("/message", methods=['POST'])
def parse():
    raw_data = request.get_json()
    data = raw_data['data']
    response = dict()
    requestTo = dict()
    command = None
    message = data['message']
    if message == '':
        return "No message", 400
    if re.fullmatch('\s*/\w+', message):
        return 'No message', 400
    if re.match('\s*/\s+', data['message']):
        return 'No command', 400
    if re.match('\s*/\w+', data['message']):
        command = re.findall(r'/\w+', data['message'])[0]
        message = data['message'].replace(command + ' ', '')
        message = " ".join(message.split())
        command = command.replace('/', '')
        server_url = get_command_url(command)
        if server_url != 0:
            requestTo["data"] = {"command": command, "message": message}
            responseSpecificServer = make_request_request(server_url, requestTo)
            return responseSpecificServer, 200
    response["data"] = {"command": command, "message": message}
    return jsonify(response), 200

@app.route("/register", methods=['POST'])
def register():
    # {"data": { "command": "shrug", "server_url": "http://shrug_command:5051"}}
    # {"data": { "command": "email", "server_url": "http://email_command:5052"}}

    raw_data = request.get_json()
    data = raw_data['data']
    command = data['command']
    server_url = data['server_url']
    new_server_url = Commands(command=command, server_url=server_url)
    db.session.add(new_server_url)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Url already exists'}), 400
    response = dict()
    response["data"] = {"command": command, "message": 'saved'}
    return jsonify(response) 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
