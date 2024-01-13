from screeps_loan import app
from screeps_loan.models.rooms import get_all_rooms
from screeps_loan.routes.decorators import httpresponse
from screeps_loan.screeps_client import get_client
from screeps_loan.services.cache import cache
import screeps_loan.models.rankings as rankings_model
import json
from flask import render_template
from flask_cors import cross_origin


@app.route("/map/rooms.js")
@cross_origin(origins="*", send_wildcard=True, methods="GET")
@httpresponse(expires=300, content_type="application/json")
def alliance_room_json():
    room_data = get_all_rooms()
    room_data_aux = {}
    for room in room_data:
        room_data_aux[room["roomname"]] = {
            "level": room["level"],
            "owner": room["owner_name"],
        }

    return json.dumps(room_data_aux)


@app.route("/map/<shard>/rooms.js")
@cross_origin(origins="*", send_wildcard=True, methods="GET")
@httpresponse(expires=300, content_type="application/json")
def alliance_room_shard_json(shard=None):
    room_data = get_all_rooms(shard=shard)
    room_data_aux = {}
    for room in room_data:
        room_data_aux[room["roomname"]] = {
            "level": room["level"],
            "owner": room["owner_name"],
        }

    return json.dumps(room_data_aux)

@app.route("/map/<shard>/alliances.js")
@cross_origin(origins="*", send_wildcard=True, methods="GET")
@httpresponse(expires=300, content_type="application/json")
def alliance_listing_json_by_shard(shard=None):
    import screeps_loan.models.alliances as alliances
    import screeps_loan.models.users as users

    alliance_query = alliances.AllianceQuery()
    all_alliances = alliance_query.getAllByShard(shard)

    alliance_users = alliance_query.getMembershipDataByShard(shard)
    alliance_user_data = {}
    for users_row in alliance_users:
        alliance_user_data[users_row["id"]] = users_row

    ranking_types = rankings_model.get_rankings_list()
    ranking_data = {}
    for ranking_type in ranking_types:
        ranking_data[ranking_type] = rankings_model.get_rankings_by_import_and_type(
            ranking_type
        )

    alliances_aux = {}
    for alliance in all_alliances:
        if not alliance["id"] in alliance_user_data:
            continue

        if alliance_user_data[alliance["id"]]["room_count"] < 1:
            continue

        alliance["members"] = alliance_user_data[alliance["id"]]["members"]
        alliance["name"] = alliance["fullname"]
        alliance["abbreviation"] = alliance["shortname"]
        alliance.pop("fullname", None)
        alliance.pop("shortname", None)

        for ranking_type in ranking_types:
            if alliance["abbreviation"] in ranking_data[ranking_type]:
                data = ranking_data[ranking_type][alliance["abbreviation"]]
                alliance[ranking_type + "_rank"] = data
        alliances_aux[alliance["abbreviation"]] = alliance

    return json.dumps(alliances_aux)


@app.route("/map/<shard>")
def map(shard):
    maxroom = get_shard_size(shard)
    return render_template(
        "map.html", alliance_url="/alliances.js", shard=shard, maxroom=maxroom
    )


@app.route("/map/<shard>/users")
def map_users(shard):
    maxroom = get_shard_size(shard)
    return render_template("map_users.html", shard=shard, maxroom=maxroom)


botmapurl = "/vk/bots/league.json"


@app.route("/map/<shard>/bots")
def map_bots(shard):
    maxroom = get_shard_size(shard)
    return render_template(
        "map.html", alliance_url=botmapurl, shard=shard, maxroom=maxroom
    )


@cache.cache()
def get_shard_size(shard):
    api = get_client()
    api_worldsize = api.worldsize(shard)
    return int((api_worldsize["width"] - 2) / 2)
