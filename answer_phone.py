from flask import Flask, request, g
from twilio.twiml.voice_response import VoiceResponse, Say
from twilio.rest import Client
import pymysql
import json
from db_handler import open_db_connection, close_db_connection, \
            sql_select, sql_execute, get_questions
from __main__ import app


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
        transcribe_response(call_id, question_list)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}    


@app.route("/getquestion", methods=['GET'])
def get_next_question(): 
    next_question = 'NONE'
    call_id = request.args.get('CallSid')
    entry = sql_select('SELECT * FROM responses WHERE rid=\"{}\"'.format(call_id))[0]
    question_list = json.loads(entry[1])
    print("Getting next question from: ")
    print(question_list)
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
    return "OK\n"


def transcribe_response(callSid, question_list):
    # For each question, save to google, then get transcription
    #for question in question_list:
    pass   


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
    
    return call

