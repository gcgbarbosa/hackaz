import os
import pyrebase
import pymysql
import json
from flask import Flask, render_template, request, redirect, url_for, g, jsonify
from db_handler import *
from twilio.twiml.voice_response import VoiceResponse, Say
from twilio.rest import Client
import json
from google.cloud import storage, speech_v1
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import urllib.request

app = Flask(__name__)

#####################################
account_sid = 'AC3e44fa4e321102d49970204274665cce'
auth_token = '1075a9192b2ecef980c681c59b21af96'
client = Client(account_sid, auth_token)
server_url = 'https://a6d899d0.ngrok.io'
say_config = { 'voice':'alice', 'lang':'en-CA' }


@app.route('/callrecording', methods=['POST', 'GET'])
def new_recording():
    recordingURL = request.args.get('RecordingUrl')
    callSid = request.args.get('CallSid')
    entry = sql_select('SELECT * FROM responses WHERE rid=\"{}\"'.format(callSid))[0]
    question_list = json.loads(entry[1])
    for question in question_list:
        if 'responseUrl' not in question or question['responseUrl'] != 'inProgress':
            continue
        else:
            question['responseUrl'] = recordingURL
            break    

    sql_execute('UPDATE responses SET questions={} WHERE rid=\"{}\"'
               .format(json.dumps(str(question_list).replace("'", '\"')),
                        callSid)
    )
    print(question_list)
    print("Updated questions!")
    done_flag = True
    # Check if we are done and need to transcribe
    for question in question_list:
        if 'responseUrl' not in question or \
            question['responseUrl'] == 'inProgress':
            done_flag = False
    if done_flag:
        transcribe_response(callSid, question_list)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}    


@app.route("/getquestion", methods=['GET'])
def get_next_question(): 
    next_question = 'NONE'
    call_id = request.args.get('CallSid')
    entry = sql_select('SELECT * FROM responses WHERE rid=\"{}\"'.format(call_id))[0]
    question_list = json.loads(entry[1])
    for question in question_list:
        if 'responseUrl' not in question:
            next_question = question['text']
            break

    response = VoiceResponse() 
    if next_question == 'NONE':
        response.say("Thank you for your time. Your recruiter will contact you if they have further questions.",
               voice=say_config['voice'], language=say_config['lang'])
        response.hangup() 
    else: 
        response.say("Please answer the following question after the beep. Press any button when you are finished.",
               voice=say_config['voice'], language=say_config['lang'])
        response.say(next_question,
               voice=say_config['voice'], language=say_config['lang'])
        question['responseUrl'] = 'inProgress'
        sql_execute('UPDATE responses SET questions={} WHERE rid=\"{}\"'
               .format(json.dumps(str(question_list).replace("'", '\"')),
                        call_id)
        )
        response.record(
               method='GET',
               timeout=0,
               max_length=120,
               trim='trim-silence',
               recording_status_callback=server_url+'/callrecording',
               recording_status_callback_method='GET'
        )
    return str(response)


@app.route("/testcall", methods=['GET', 'POST'])
def test_call():
    send_schedule_link('15038808741', 'testhash')
    return "OK\n"


def transcribe_response(callSid, question_list):
    # For each question, save to google, then get transcription
    storage_client = storage.Client()
    speech_client = speech_v1.SpeechClient()
    speech_config = {
                    "sample_rate_hertz": 8000,
                    "language_code": "en-US"
                    }
    audio_uri = {'uri': ''}
    bucket_name = "hackaz-265516.appspot.com"
    bucket = storage_client.bucket(bucket_name)
    for question in question_list:
        if 'responseUrl' in question and \
         question['responseUrl'] != 'inProgress':
            recording_url = question['responseUrl']
            output_file_name = str(callSid)+"_"+str(question['id_question'])+".wav"
            with urllib.request.urlopen(recording_url) as response,\
             open(output_file_name, "wb") as out_file:
                data = response.read()
                out_file.write(data)
            blob = bucket.blob(output_file_name)
            blob.upload_from_filename(output_file_name)
            os.remove(output_file_name)
            
            audio_uri['uri'] = 'gs://'+bucket_name+'/'+output_file_name
            response = speech_client.recognize(speech_config, audio_uri)
            transcript = ''
            for result in response.results:
                transcript = result.alternatives[0].transcript
                break
            question['transcript'] = transcript
    
    # Send emails using transcriptions + questions
    email_info = sql_select('select Iemail, name from positions pos inner join (select name, Ppid from application app inner join (select Aphone, Ppid from app_pos ap where ap.Rrid="{}") as T1  on T1.Aphone=app.phone) as T2 on pos.pid=T2.Ppid'
        .format(str(callSid)))
    email_to = email_info[0][0]
    email_from = 'assistant@aiscreen.tech'
    email_subject = email_info[0][1]+' Phone Screen Answers'
    email_body = 'Phone Screen Answers for Applicant: '+email_info[0][1]
    email_body += '<br><br>'
    for question in question_list:
        if 'transcript' in question:
            email_body += '<b>'+question['text']+'</b><br>'
            email_body += 'Answer: '+question['transcript']+'<br><br>'
    try:
        message = Mail(
            from_email=email_from,
            to_emails=email_to,
            subject=email_subject,
            html_content=email_body
        )
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(str(e))


def start_call(Aphone, position_id): 
    call = client.calls.create(
            url=server_url+'/getquestion',
            method='GET',
            to='+'+str(Aphone),
            from_='+12054481748'
    )
    
    # Create response entry
    open_db_connection()
    q_list = get_questions(position_id)
    open_db_connection()
    with g.db.cursor() as cursor:
        json_q_list = json.dumps(str(q_list).replace("'", '\"'))
        cursor.execute(
            'INSERT INTO responses (rid, questions) VALUES (\"{}\", {})'
                .format(call.sid, json_q_list))
        g.db.commit()
    open_db_connection()
    with g.db.cursor() as cursor:
        cursor.execute(
            'UPDATE app_pos SET Rrid=\"{}\" WHERE Aphone=\"{}\" AND Ppid={}'
                .format(call.sid, str(Aphone), str(position_id)))
        g.db.commit()
         
    return call
#####################################

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
    #mock()
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


@app.route('/new_user/<p_id>/<name>/<phone>')
def new_user(p_id, name, phone):
    data = {}
    #return str(question)
    #insert_update_question(int(p_id), question)
    data["name"] = name
    data["phone"] = phone

    insert_update_candidate(p_id, data)

    return jsonify(success=True)

@app.route('/edit_question/<p_id>/<question>/<question_id>')
def edit_question(p_id, question, question_id):
    #return str(question)
    insert_update_question(int(p_id), question, question_id)
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

@app.route('/make_calls', methods=['GET', 'POST'])
def make_calls():
    calls = get_calls()
    print(calls)
    if len(calls) > 0:    
        phone = calls[0][0]
        id_position = calls[0][1]    
        answer_phone.start_call(phone, id_position)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}    

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
