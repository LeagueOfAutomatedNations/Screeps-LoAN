from flask import Flask, session, redirect, url_for, escape, request, render_template
app = Flask(__name__)
app.config.from_envvar('SETTINGS')

import screepsapi.screepsapi as screepsapi
from auth_user import AuthPlayer
import socket
from db import get_conn


@app.route('/')
def index():
    #if 'username' in session:
    #    return 'Logged in as %s' % escape(session['username'])
    #return 'You are not logged in'
    if ('username' in session):
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #TODO: Authenticate via url
        username = request.form['username']
        user = app.config['API_USERNAME']
        password = app.config['API_PASSWORD']
        api = screepsapi.API(user, password)
        auth = AuthPlayer(api)
        (id, token) = auth.auth_token(username)
        if (id is not None):
            api.msg_send(id, url_for('auth', token=token, _external=True))
        return redirect(url_for('auth_request'))
    return render_template("login.html")

@app.route('/auth/success')
def auth_request():
    return render_template('auth_sent.html')
@app.route('/auth/<token>')
def auth(token):
    query = "SELECT ign FROM users WHERE login_code=%s"
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(query, (token,))
    row = cursor.fetchone()
    if (row is not None):
        session['username'] = row[0]

    return redirect(url_for('index'))

@app.route('/logout', methods = ["GET", "POST"])
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
