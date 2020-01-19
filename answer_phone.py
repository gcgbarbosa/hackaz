from flask import Flask, request, Blueprint, render_template, abort
from twilio.twiml.voice_response import VoiceResponse, Say
from twilio.rest import Client
import pymysql
import json



account_sid = 'AC3e44fa4e321102d49970204274665cce'
auth_token = '1075a9192b2ecef980c681c59b21af96'
client = Client(account_sid, auth_token)
server_url = 'https://41ea7ffd.ngrok.io'
say_config = { 'voice':'alice', 'lang':'en-CA' }
db_user = "root"
db_password = "cluivilab"
db_connection = pymysql.connect(user="root", password="cluivilab", host="127.0.0.1", db="hackaz_db")

@app.route('/callrecording', methods=['POST', 'GET'])
def new_recording():
    #TODO transcribe and save in database
    print("Entering new_recording...")
    print('  Callsid: '+request.args.get('CallSid'))
    print('  RecordingUrl: '+request.args.get('RecordingUrl'))
    recordingSid = request.args.get('RecordingSid')
    recordingURL = request.args.get('RecordingUrl')
    callSid = request.args.get('CallSid')
    duration = request.args.get('RecordingDuration')
    status = request.args.get('RecordingStatus')

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}    


@app.route("/callcomplete", methods=['POST', 'GET'])
def call_complete():
    #TODO save recording Url 'responses' table
    print("Entering call_complete...")
    print('  CallSid: '+request.args.get('CallSid'))
    print('  RecordingUrl: '+request.args.get('RecordingUrl'))
    response = VoiceResponse()
    response.say("Thank you for your time. Your recruiter will contact you if they have further questions.",
                voice=say_config['voice'], language=say_config['lang'])
    response.hangup()
    return str(response)


@app.route("/getquestion", methods=['GET'])
def get_next_question(): 
    #TODO parse user info from GET
    call_id = request.args.get('CallSid')
    with db_connection.cursor() as cursor:
        cursor.execute('SELECT '+str(call_id)+' FROM responses;')
        entry = cursor.fetchall()
    
    
    response = VoiceResponse()
    response.say("Please answer the following question after the beep. Press any button when you are finished.",
               voice=say_config['voice'], language=say_config['lang'])
    response.pause(1)
    response.say(question,
               voice=say_config['voice'], language=say_config['lang'])
    response.record(
               action=server_url+'/callcomplete',
               method='GET',
               timeout=0,
               max_length=120,
               trim='trim-silence',
               recording_status_callback=server_url+'/callrecording',
               recording_status_callback_method='GET'
    )
    print(str(response))
    print("\nFinished 'get_xml()'\n")
    return str(response)


def start_call(Aphone, position_id): #TODO parse json from database 
    call = client.calls.create(
            url=server_url+'/getquestion',
            method='GET',
            to='+'+str(Aphone),
            from_='+12054481748'
           )
    #Create response entry
    with db_connection.cursor() as cursor:
        cursor.execute('INSERT INTO responses (rid) values ('+str(call.sid)+')')
    return call.sid
