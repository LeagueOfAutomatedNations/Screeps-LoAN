from screeps_loan import app
import screeps_loan.models.alliances as alliances
from screeps_loan.models.rooms import get_all_rooms
import screeps_loan.models.users as users_model
import json
from flask import render_template


@app.route('/a/<shortname>')
def alliance_profile(shortname):
    room_data = get_all_rooms()
    room_data_aux = {}
    for room in room_data:
        room_data_aux[room['roomname']] = {'level': room['level'], 'owner': room['owner_name']}

    users = users_model.find_name_by_alliance(shortname)
    users_aux = {}
    for user in users:
        users_aux['user'] = {"members": [user], "name": user}
    return render_template("alliance_profile.html", room_data = json.dumps(room_data_aux),
                           alliance_data = json.dumps(users_aux));
    
