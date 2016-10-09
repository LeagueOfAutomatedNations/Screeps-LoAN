from screeps_loan import app
from screeps_loan.models.rooms import get_all_rooms
import json
from flask import render_template


@app.route('/map/rooms.js')
def alliance_room_json():
    room_data = get_all_rooms()
    room_data_aux = {}
    for room in room_data:
        room_data_aux[room['roomname']] = {'level': room['level'], 'owner': room['owner_name']}

    return json.dumps(room_data_aux)


@app.route('/map')
def map():
    return render_template("map.html", alliance_url='/alliances.js')
