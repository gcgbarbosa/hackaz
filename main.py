import os
import pyrebase
import pymysql
import json
from flask import Flask, render_template, request
from db_handler import *

app = Flask(__name__)

import answer_phone

config = {
    "apiKey": "AIzaSyD5WuKixyIe9hx2CthXRAWr9gRPWdulq_U",
    "authDomain": "hackaz-265516.firebaseapp.com",
    "databaseURL": "https://hackaz-265516.firebaseio.com",
    "projectId": "hackaz-265516",
    "storageBucket": "hackaz-265516.appspot.com",
    "messagingSenderId": "64563442156",
    "appId": "1:64563442156:web:52e9134235636bf4dad0c9"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

def mock():
	print("Candidates")
	print(get_candidates(12))
    #create_interviewer("pelovett@gmail.com", "Peter Lovett")
    #create_interviewer("pelovett@gmail.com", "Peter Lovett")
    # id_position = create_position("Software Development", 0, "pelovett@gmail.com", "Code some stuff")
    # create_question(id_position, "Whats your name?")
    # create_question(id_position, "How old are you?")
    # data = {"phone":"15038808741", "name":"Peter Lovett"}
    # create_candidate(id_position, data)
    # data = {"phone":"15207885673", "name":"Paulo Soares"}
    # create_candidate(id_position, data)
    #get_questions(12)

@app.before_request
def before_request():
    open_db_connection()
    
@app.after_request
def after_request(response):
    close_db_connection()
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    mock()
    if (request.method == 'POST'):
        email = request.form['email']
        password = request.form['password']
        try:
            auth.sign_in_with_email_and_password(email, password)
        #user_id = auth.get_account_info(user['idToken'])
        #session['usr'] = user_id            
            return render_template('dashboard.html')
        except:
            #unsuccessful = 'Please check your credentials'
            #return render_template('index.html', umessage=unsuccessful)
            pass
    return render_template('index.html')

@app.route('/manage_process', methods=['GET', 'POST'])
def manage_process():
    if request.method == 'POST':
        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    hiring = {}
    hiring["position"] = "Software Development"
    hiring["description"] = "Position X"
    hiring["id"] = 1123
    hiring["questions"] = []
    hiring["candidates"] = []
    for i in range(4):        
        question = {"id": i, "text": "Question " + str(i)}
        hiring["questions"].append(question)
    for i in range(2):        
        candidate = {"id": i, "name": "Candidate" + str(i), "phone":"111111111111"}
        hiring["candidates"].append(candidate)
    return render_template('manage_process.html', hiring=hiring)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)