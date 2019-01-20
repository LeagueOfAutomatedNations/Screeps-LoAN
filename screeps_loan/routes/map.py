from screeps_loan import app
from screeps_loan.models.rooms import get_all_rooms
from screeps_loan.routes.decorators import httpresponse
from screeps_loan.screeps_client import get_client
from screeps_loan.services.cache import cache
import json
from flask import render_template
from flask_cors import cross_origin

@app.route('/map/rooms.js')
@cross_origin(origins="*", send_wildcard=True, methods="GET")
@httpresponse(expires=300, content_type='application/json')
def alliance_room_json():
    room_data = get_all_rooms()
    room_data_aux = {}
    for room in room_data:
        room_data_aux[room['roomname']] = {'level': room['level'], 'owner': room['owner_name']}

    return json.dumps(room_data_aux)


@app.route('/map/<shard>/rooms.js')
@cross_origin(origins="*", send_wildcard=True, methods="GET")
@httpresponse(expires=300, content_type='application/json')
def alliance_room_shard_json(shard=None):
    room_data = get_all_rooms(shard=shard)
    room_data_aux = {}
    for room in room_data:
        room_data_aux[room['roomname']] = {'level': room['level'], 'owner': room['owner_name']}

    return json.dumps(room_data_aux)



@app.route('/map/<shard>')
def map(shard):
    maxroom = get_shard_size(shard)
    return render_template("map.html", alliance_url='/alliances.js', shard=shard, maxroom=maxroom)


@app.route('/map/<shard>/users')
def map_users(shard):
    maxroom = get_shard_size(shard)
    return render_template("map_users.html", shard=shard, maxroom=maxroom)


botmapurl = '/vk/bots/league.json'
@app.route('/map/<shard>/bots')
def map_bots(shard):
    maxroom = get_shard_size(shard)
    return render_template("map.html", alliance_url=botmapurl, shard=shard, maxroom=maxroom)


@cache.cache()
def get_shard_size(shard):
    api = get_client()
    api_worldsize = api.worldsize(shard)
    return int((api_worldsize['width']-2)/2)
