import os
import pyrebase
import pymysql
from flask import Flask, render_template, request
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
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()


def print_questions():
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user, password=db_password,
                              unix_socket=unix_socket, db=db_name)
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        host = '127.0.0.1'
        cnx = pymysql.connect(user=db_user, password=db_password,
                              host=host, db=db_name)

    with cnx.cursor() as cursor:
        cursor.execute('SELECT NOW() as now;')
        result = cursor.fetchall()
        current_time = result[0][0]
    cnx.close()

    print('yes')
    print(str(current_time))
	

@app.route('/', methods=['GET', 'POST'])
def index():
    print_questions()
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
    return render_template('manage_process.html')

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)