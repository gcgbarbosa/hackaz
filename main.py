import os
import pyrebase
import pymysql
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
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

def get_linux_epoch(scheduled_date):
    return 4

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
            #return render_template('dashboard.html')
            #redirect the user to /dashboard
            return redirect('/dashboard')
        except:
            #unsuccessful = 'Please check your credentials'
            #return render_template('index.html', umessage=unsuccessful)
            pass
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # get get the list of processes from the database
    
    # pass the list of processes to the database
    positions = get_positions()
     
    return render_template('dashboard.html', positions=positions)


@app.route('/manage_process/<process_id>')
def manage_process(process_id):
    # retrieve the information about the position
    position = get_position(process_id)

    ## list all questions of a project
    questions = get_questions(process_id)

    ## list all the candidates of a project
    candidates = get_candidates(process_id)
    #return str(candidates)

    return render_template('manage_process.html', position=position, questions=questions, candidates=candidates)

    ###############################
    if request.method == 'POST':
        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))

    # TODO - Load the hiring processes for that employee

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
    

@app.route('/schedule_interview/<token>')
def schedule_interview(token):
    return render_template('schedule_interview.html', token=token)

@app.route('/confirm_schedule/<token>/<linux_epoch>')
def confirm_schedule(token, linux_epoch):
    # check if the token is in the database
    if check_token(token):
        # add the linux_epoch to the database
        # return status 200
        return jsonify(success=True)
    else:
        return jsonify(success=False)
    #return token + ' ' + linux_epoch

@app.route('/new_question/<p_id>/<question>')
def new_question(p_id, question):
    #return str(question)
    insert_update_question(int(p_id), question)
    return jsonify(success=True)

@app.route('/conf_create_question', methods=['POST'])
def conf_create_question():
    id_position = 0
    text = ""
    create_question(id_position, text)
    redirect(url_for('manage_process'))    

@app.route('/conf_remove_question', methods=['POST'])
def conf_remove_question():
	id_position = 0
	id_question = 0
	remove_question(id_position, id_question)
	redirect(url_for('manage_process')) 

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
