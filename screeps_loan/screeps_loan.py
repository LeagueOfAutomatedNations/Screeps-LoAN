from flask import Flask, session, redirect, url_for, escape, request, render_template, flash, send_from_directory
from screeps_loan import app
app.config.from_envvar('SETTINGS')

import socket
import screeps_loan.cli.import_user
import screeps_loan.cli.maintenance

import screeps_loan.routes.auth
import screeps_loan.routes.alliances
import screeps_loan.routes.my_alliance

@app.route('/obj/<filename>')
def get_obj(filename):
    return send_from_directory(app.config['OBJECT_STORAGE'], filename)

@app.route('/')
def index():
    return redirect(url_for('map'))

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


# set the secret key.  keep this really secret:
app.secret_key = app.config['SECRET_KEY']
