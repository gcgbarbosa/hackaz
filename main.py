import os
import pyrebase
import pymysql
import json
from flask import Flask, render_template, request, g
app = Flask(__name__)

config = {
    "apiKey": "AIzaSyD5WuKixyIe9hx2CthXRAWr9gRPWdulq_U",
    "authDomain": "hackaz-265516.firebaseapp.com",
    "databaseURL": "https://hackaz-265516.firebaseio.com",
    "projectId": "hackaz-265516",
    "storageBucket": "hackaz-265516.appspot.com",
    "messagingSenderId": "64563442156",
    "appId": "1:64563442156:web:52e9134235636bf4dad0c9"
}

db_user = "root"#os.environ.get('CLOUD_SQL_USERNAME')
db_password = "cluivilab"#os.environ.get('CLOUD_SQL_PASSWORD')
db_name = "hackaz_db"#os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

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
    cursor = g.db.cursor()
    insert_statement = "INSERT INTO application (name, phone) VALUES (\"{}\",\"{}\")".format(data["name"], data["phone"])
    cursor.execute(insert_statement)

# def create_response(data):
#     cursor = g.db.cursor()
#     insert_statement = "INSERT INTO application (name, phone) VALUES (\"{}\",\"{}\")".format(data.name, data.phone)
#     cursor.execute(insert_statement)
#     return g.db.insert_id()

def create_candidate(id_position, data):
    create_application(data)
    cursor = g.db.cursor()
    # TODO 
    hash = "123456"
    #insert_statement = "INSERT INTO app_pos (Aphone, Ppid, hash) VALUES (\"{}\", {}, \"{}\") ON DUPLICATE KEY UPDATE hash = \"{}\" WHERE Aphone = \"{}\" AND Ppid = {}".format(data["phone"], id_position, hash, hash, data["phone"], id_position)
    insert_statement = "INSERT INTO app_pos (Aphone, Ppid, hash) VALUES (\"{}\", {}, \"{}\")".format(data["phone"], id_position, hash)
    cursor.execute(insert_statement)        

def update_candidate(id_position, id_candidate, data):
    cursor = g.db.cursor()
    update_statement = "UPDATE application SET name = \"{}\" WHERE phone=\"{}\"".format(data['name'], data['phone'])
    cursor.execute(update_statement)

def create_question(id_position, text):
    questions = get_questions(id_position)
    new_question = {"id_question":len(questions)+1, "text":text}
    questions.append(new_question)
    cursor = g.db.cursor()
    insert_statement = "UPDATE positions SET questions='{}' WHERE pid={}".format(json.dumps(questions), id_position)
    cursor.execute(insert_statement)

def update_question(id_position, id_question, new_text):
    questions = get_questions(id_position)
    for question in questions:
        question.update((id, new_text) for id, _ in question.iteritems() if id == id_question)
    cursor = g.db.cursor()
    update_statement = "UPDATE positions SET questions=\"{}\" WHERE pid={}".format(json.dumps(questions), id_position)
    cursor.execute(update_statement)

def create_position(title, progress, Iemail, description):
    cursor = g.db.cursor()
    insert_statement = "INSERT INTO positions (title, progress, Iemail, description) VALUES (\"{}\",{},\"{}\",\"{}\")".format(title, progress, Iemail, description)
    cursor.execute(insert_statement)
    return g.db.insert_id()

def update_position(id_position, title, progress, Iemail, description):
    cursor = g.db.cursor()
    update_statement = "UPDATE positions SET title = \"{}\", progress = {}, Iemail = \"{}\", description = \"{}\" WHERE id_position = {}".format(id_position, title, progress, Iemail, description)
    cursor.execute(update_statement)

def create_interviewer(email, name):
    cursor = g.db.cursor()
    insert_statement = "INSERT INTO interviewer (email, name) VALUES (\"{}\",\"{}\")".format(email, name)
    cursor.execute(insert_statement)
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
    cursor = g.db.cursor()
    update_statement = "UPDATE positions SET questions=\"{}\" WHERE pid={}".format(json.dumps(questions), id_position)
    cursor.execute(update_statement)

def get_questions(id_position):
    return []

def get_candidates(id_position):
    pass

def mock():
    #create_interviewer("pelovett@gmail.com", "Peter Lovett")
    id_position = create_position("Software Development", 0, "pelovett@gmail.com", "Code some stuff")
    create_question(id_position, "Whats your name?")
    create_question(id_position, "How old are you?")
    data = {"phone":"15038808741", "name":"Peter Lovett"}
    create_candidate(id_position, data)
    data = {"phone":"15207885673", "name":"Paulo Soares"}
    create_candidate(id_position, data)
    g.db.commit()

# @app.before_request
# def before_request():
#     open_db_connection()
    
# @app.after_request
# def after_request(response):
#     close_db_connection()
#     return response

@app.route('/', methods=['GET', 'POST'])
def index():
    open_db_connection()
    mock()
    close_db_connection()
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