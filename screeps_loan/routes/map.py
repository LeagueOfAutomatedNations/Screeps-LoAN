from screeps_loan import app
from screeps_loan.models.rooms import get_all_rooms
from screeps_loan.routes.decorators import httpresponse
import json
from flask import render_template
@cross_origin()

@app.route('/map/rooms.js')
@httpresponse(expires=300, content_type='application/json')
def alliance_room_json():
    room_data = get_all_rooms()
    room_data_aux = {}
    for room in room_data:
        room_data_aux[room['roomname']] = {'level': room['level'], 'owner': room['owner_name']}

    return json.dumps(room_data_aux)


@app.route('/map')
def map():
    return render_template("map.html", alliance_url='/alliances.js')


@app.route('/map/users')
def map_users():
    return render_template("map_users.html")
