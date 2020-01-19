from flask import Flask, request, g
from twilio.twiml.voice_response import VoiceResponse, Say
from twilio.rest import Client
import pymysql
import json
from db_handler import open_db_connection, close_db_connection, \
            sql_select, sql_execute, get_questions
from __main__ import app
from google.cloud import storage, speech_v1
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import urllib.request

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
    call_id = start_call(15038808741, 16)
    #call_id = "CAe5a777f6971645aefb221f3ec3794f63"
    #q_list = "[{'text': 'Whats your name?', 'id_question': 1, 'responseUrl': 'https://api.twilio.com/2010-04-01/Accounts/AC3e44fa4e321102d49970204274665cce/Recordings/REb68625bfd59e89afddb1cd8b504d5a58'}, {'text': 'How old are you?', 'id_question': 2, 'responseUrl': 'https://api.twilio.com/2010-04-01/Accounts/AC3e44fa4e321102d49970204274665cce/Recordings/RE1ffdfc810a3e0e252c27fe212e5ef70a'}]" 
    #q_list = json.loads(q_list.replace("'", '\"'))
    #transcribe_response(call_id, q_list) 
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

