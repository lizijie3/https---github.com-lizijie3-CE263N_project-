from distutils.cmd import Command
from email import message
from flask import Flask, request, Response, jsonify
import json

app = Flask(__name__)
11  1111
@app.route("/command", methods=['POST'])
def command():
    raw_data = request.get_json()
    data = raw_data['data']
    message = data['message']
    response = dict()
    if data['command'] != 'shrug':
        return {}, 400
    message = message + '¯\_(ツ)_/¯'
    response["data"] = {"command": 'shrug', "message": message} 
    return response, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5051)