import os
import pymysql
import json
from twilio.rest import Client
from flask import g
import hashlib
import datetime

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

account_sid = 'AC3e44fa4e321102d49970204274665cce'
auth_token = '1075a9192b2ecef980c681c59b21af96'
client = Client(account_sid, auth_token)

def sql_select(query):
    data = []
    open_db_connection()
    with g.db.cursor() as cursor:
        cursor.execute(query)
    g.db.commit()
    data = cursor.fetchall()
    return data

def sql_execute(statement):
    data = []
    open_db_connection()
    with g.db.cursor() as cursor:
        cursor.execute(statement)
    g.db.commit()
    return data

def open_db_connection():
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        g.db = pymysql.connect(user=db_user, password=db_password,
                              unix_socket=unix_socket, db=db_name)
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        host = '127.0.0.1'
        g.db = pymysql.connect(user=db_user, password=db_password,
                              host=host, db=db_name)

def close_db_connection():
    if g.db is not None:
        g.db.close()

def create_application(data):
    with g.db.cursor() as cursor:
        insert_statement = "INSERT INTO application (name, phone) VALUES (\"{0}\",\"{1}\") ON DUPLICATE KEY UPDATE name= \"{0}\"".format(data["name"], data["phone"])
        cursor.execute(insert_statement)
    g.db.commit()

def create_candidate(id_position, data):
    create_application(data)
    with g.db.cursor() as cursor:
        hash = hashlib.md5(os.urandom(32)).hexdigest()
        insert_statement = "INSERT INTO app_pos (Aphone, Ppid, hash) VALUES (\"{}\", {}, \"{}\")".format(data["phone"], id_position, hash)
        cursor.execute(insert_statement) 
    g.db.commit()       
    send_schedule_link(data["phone"], hash)

def send_schedule_link(phone_num, hash_code):
    message = client.messages.create(
                body='Hi, please schedule your phone screening: https://hackaz-265516.appspot.com/schedule_interview/'+hash_code,
                from_='+12054481748',
                to='+'+str(phone_num)
    )

def update_candidate(id_position, id_candidate, data):
    with g.db.cursor() as cursor:
        update_statement = "UPDATE application SET name = \"{}\" WHERE phone=\"{}\"".format(data['name'], data['phone'])
        cursor.execute(update_statement)
    g.db.commit()

def create_question(id_position, text):
    questions = get_questions(id_position)
    new_question = {"id_question":len(questions)+1, "text":text}
    questions.append(new_question)
    with g.db.cursor() as cursor:
        insert_statement = "UPDATE positions SET questions='{}' WHERE pid={}".format(json.dumps(questions), id_position)
        cursor.execute(insert_statement)
    g.db.commit()

def update_question(id_position, id_question, new_text):
    questions = get_questions(id_position)
    for question in questions:
        if question['id_question'] == id_question:             
            question["text"] = new_text

    with g.db.cursor() as cursor:
        update_statement = "UPDATE positions SET questions=\'{}\' WHERE pid={}".format(json.dumps(questions), id_position)
        cursor.execute(update_statement)
    g.db.commit()

def create_position(title, progress, Iemail, description):
    with g.db.cursor() as cursor:
        insert_statement = "INSERT INTO positions (title, progress, Iemail, description) VALUES (\"{}\",{},\"{}\",\"{}\")".format(title, progress, Iemail, description)
        cursor.execute(insert_statement)
    g.db.commit()
    return g.db.insert_id()

def update_position(id_position, title, progress, Iemail, description):
    with g.db.cursor() as cursor:
        update_statement = "UPDATE positions SET title = \"{}\", progress = {}, Iemail = \"{}\", description = \"{}\" WHERE id_position = {}".format(id_position, title, progress, Iemail, description)
        cursor.execute(update_statement)
    g.db.commit()

def create_interviewer(email, name):
    with g.db.cursor() as cursor:
        insert_statement = "INSERT INTO interviewer (email, name) VALUES (\"{}\",\"{}\")".format(email, name)
        cursor.execute(insert_statement)
    g.db.commit()
    return g.db.insert_id()    

def insert_update_candidate(id_position, data, id_candidate=None):
    if id_candidate == None:
        create_candidate(id_position, data)
    else:
        update_candidate(id_position, id_candidate, data)

def insert_update_question(id_position, text, id_question=None):
    if id_question == None:
        create_question(id_position, text)
    else:
        update_question(id_position, id_question, text)

def remove_question(id_question, id_position):
    questions = get_questions(id_position)
    questions = [question for question in questions if not (question['id_question'] == id_question)] 
    with g.db.cursor() as cursor:
        update_statement = "UPDATE positions SET questions=\"{}\" WHERE pid={}".format(json.dumps(questions), id_position)
        cursor.execute(update_statement)
    g.db.commit()

def get_questions(id_position):
    with g.db.cursor() as cursor:
        sql = "SELECT questions FROM positions WHERE pid =\"{}\"".format(id_position)
        cursor.execute(sql)
    questions_json = cursor.fetchone()[0]
    if questions_json == None:
    	return []
    else:
    	return json.loads(questions_json)

def get_candidates(id_position):
    with g.db.cursor() as cursor:
        sql = "SELECT app_pos.Aphone, application.name FROM app_pos, application WHERE app_pos.Ppid =\"{}\" AND app_pos.Aphone = application.phone".format(id_position)
        cursor.execute(sql)
    return list(cursor.fetchall())


def get_positions():
    with g.db.cursor() as cursor:
        sql = "SELECT * FROM positions"
        cursor.execute(sql)
    return list(cursor.fetchall())

def get_position(id_position):
    with g.db.cursor() as cursor:
        sql = "SELECT * FROM positions WHERE pid = " + str(id_position)
        cursor.execute(sql)
    return list(cursor.fetchone())

def check_token(token):
    with g.db.cursor() as cursor:
        sql = "SELECT hash, COUNT(*) FROM app_pos WHERE hash=\"{}\"".format(token)
        try:
    	    cursor.execute(sql)
    	    return True
        except:
            return False

def update_scheduling(token, linux_epoch):
    with g.db.cursor() as cursor:
        update_statement = "UPDATE app_pos SET hash='', epoch=\"{}\" WHERE hash=\"{}\"".format(linux_epoch, token)
        cursor.execute(update_statement)
    g.db.commit()

def get_calls():
    epoch_now = int(datetime.datetime.now().timestamp())
    with g.db.cursor() as cursor:
        sql = "SELECT Aphone, Ppid FROM app_pos WHERE epoch < {} AND Rrid IS NULL".format(epoch_now)
        cursor.execute(sql)
    g.db.commit()
    return list(cursor.fetchall())





