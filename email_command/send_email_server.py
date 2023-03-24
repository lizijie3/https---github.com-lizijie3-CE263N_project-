from flask import Flask, request
import json
import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

@app.route('/command', methods = ['POST'])
def command():

    if request.headers.get("Content-Type") == 'application/json':

        data = request.get_json()
        data = data['data']
        command = data['command']
        if command != 'email':
            return "Invalid Command", 400
        message = data['message']
        if message == '' or len(message.split(' ')) < 3:
            return "Invalid Message", 400
        to_email = message.split(' ')[0]
        from_email = "lizijie3@berkeley.edu"
        subject = message.split(' ')[1]
        body = message.split(subject + ' ')[1]
        response = dict()
        response_code = 401
        if not to_email or not from_email or not subject or not body:
            response = {"message": "Please fill out all fields to send an email"}
            response_code = 400           
        else:
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=body)
            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                sg.send(message)
                response['data'] = {"command": "email", "message": "Email was sent"}
                response_code = 200
            except Exception as e:
                logging.error(e)
    else:
        response = {"message": "Endpoint requires json input"}
        response_code = 400 
    
    return json.dumps(response), response_code

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5052)