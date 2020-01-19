import os
import pymysql
import json
from flask import g

db_user = "root"#os.environ.get('CLOUD_SQL_USERNAME')
db_password = "cluivilab"#os.environ.get('CLOUD_SQL_PASSWORD')
db_name = "hackaz_db"#os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')


def sql_select(query):
    data = []
    open_db_connection()
    with g.db.cursor() as cursor:
        cursor.execute(query)
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
        # TODO 
        hash = "123456"
        #insert_statement = "INSERT INTO app_pos (Aphone, Ppid, hash) VALUES (\"{}\", {}, \"{}\") ON DUPLICATE KEY UPDATE hash = \"{}\" WHERE Aphone = \"{}\" AND Ppid = {}".format(data["phone"], id_position, hash, hash, data["phone"], id_position)
        insert_statement = "INSERT INTO app_pos (Aphone, Ppid, hash) VALUES (\"{}\", {}, \"{}\")".format(data["phone"], id_position, hash)
        cursor.execute(insert_statement) 
    g.db.commit()       

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
        question.update((id, new_text) for id, _ in question.iteritems() if id == id_question)
    with g.db.cursor() as cursor:
        update_statement = "UPDATE positions SET questions=\"{}\" WHERE pid={}".format(json.dumps(questions), id_position)
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

def insert_update_candidate(id_position, id_candidate, data):
    if id_candidate == None:
        create_candidate(id_position, data)
    else:
        update_candidate(id_position, id_candidate, data)

def insert_update_question(id_position, id_question, text):
    if id_candidate == None:
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







