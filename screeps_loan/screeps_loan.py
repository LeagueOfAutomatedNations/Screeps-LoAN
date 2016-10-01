from flask import Flask, session, redirect, url_for, escape, request, render_template
from screeps_loan import app
app.config.from_envvar('SETTINGS')

import screepsapi.screepsapi as screepsapi
from screeps_loan.auth_user import AuthPlayer
import socket
from screeps_loan.models.db import get_conn
import screeps_loan.screeps_client as screeps_client
import screeps_loan.cli.import_user


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
        api = screeps_client.get_client()
        auth = AuthPlayer(api)
        (id, token) = auth.auth_token(username)
        if (id is not None):
            api.msg_send(id, url_for('auth', token=token, _external=True))
        return redirect(url_for('auth_request'))
    return render_template("login.html")

@app.route('/alliances')
def alliance_listing():
    import screeps_loan.models.alliances as alliances
    import screeps_loan.models.users as users

    alliance_query = alliances.AllianceQuery()
    all_alliances = alliance_query.getAll()
    alliances_name = [item["shortname"] for item in all_alliances]
    users_with_alliance = users.UserQuery().find_name_by_alliances(alliances_name)
    for alliance in all_alliances:
        alliance['users'] = [user for user in users_with_alliance if user['alliance'] == alliance['shortname']]
    return render_template("alliance_listing.html", alliances = all_alliances)


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
