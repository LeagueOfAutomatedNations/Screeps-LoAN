from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from screeps_loan import app
app.config.from_envvar('SETTINGS')

import screepsapi.screepsapi as screepsapi
from screeps_loan.auth_user import AuthPlayer
import socket
from screeps_loan.models.db import get_conn
import screeps_loan.screeps_client as screeps_client
import screeps_loan.cli.import_user

import screeps_loan.routes.auth
import screeps_loan.routes.alliances
import screeps_loan.routes.my_alliance
@app.route('/')
def index():
    #if 'username' in session:
    #    return 'Logged in as %s' % escape(session['username'])
    #return 'You are not logged in'
    if ('username' in session):
        return redirect(url_for('alliance_listing'))
    return redirect(url_for('login'))

@app.route('/my')
def my_alliance():
    if ('username' not in session):
        return redirect(url_for('login'))
    return render_template('my.html')


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

@app.route('/map')
def map():
    import screeps_loan.models.alliances as alliances
    from screeps_loan.models.rooms import get_all_rooms
    import screeps_loan.models.users as users

    room_data = get_all_rooms()
    #room_data = [{item['roomname']: {'level': item['level'], 'owner': item['owner_name']}} for item in room_data]
    room_data_aux = {}
    for room in room_data:
        room_data_aux[room['roomname']] = {'level': room['level'], 'owner': room['owner_name']}

    alliance_query = alliances.AllianceQuery()
    all_alliances = alliance_query.getAll()
    alliances_name = [item["shortname"] for item in all_alliances]
    users_with_alliance = users.UserQuery().find_name_by_alliances(alliances_name)

    alliances_aux = {}
    for alliance in all_alliances:
        alliance['members'] = [user['name'] for user in users_with_alliance
                             if user['alliance'] == alliance['shortname']]
        alliances_aux[alliance['shortname']]=alliance
        alliance['name'] = alliance['fullname']
        alliance['abbreviation'] = alliance['shortname']
        alliance.pop('fullname', None)
        alliance.pop('shortname', None)
    import json
    return render_template("map.html", room_data = json.dumps(room_data_aux), alliance_data = json.dumps(alliances_aux))

@app.route('/invite', methods=["POST"])
def invite_to_alliance():
    import screeps_loan.models.users as users_model
    import screeps_loan.services.users as users_service
    import hashlib

    my_id = session['my_id']
    alliance = users_model.alliance_of_user(my_id)
    if (alliance is None):
        return "You are not in an alliance, can't invite anyone"

    username = request.form['username']
    api = screeps_client.get_client()

    auth = AuthPlayer(api)
    id = auth.id_from_name(username)
    users_model.update_alliance_by_screeps_id(id, alliance['shortname'])
    #(id, token) = auth.auth_token(username)

    #if (id is not None):
    #    api.msg_send(id, "You are invited to join %s, click for more info: \n\n" % alliance+
    #                 url_for('accept_alliance_invite', token=token, _external=True))
    flash('Successfully add user to your alliance')
    return redirect(request.referrer)

@app.route('/invite/accept/<token>')
def accept_alliance_invite(token):
    pass

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



@app.route('/logout', methods = ["GET", "POST"])
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = app.config['SECRET_KEY']
