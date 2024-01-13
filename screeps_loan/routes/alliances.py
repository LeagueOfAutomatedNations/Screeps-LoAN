from screeps_loan import app
import screeps_loan.models.alliances as alliances_model
import screeps_loan.models.rankings as rankings_model
from screeps_loan.models.rooms import get_all_rooms
import screeps_loan.models.users as users_model
from screeps_loan.services.cache import cache
from screeps_loan.screeps_client import get_client
from screeps_loan.routes.decorators import httpresponse
import json
from flask import render_template
from flask_cors import cross_origin
from screeps_loan.routes.errors import show_error

@app.route("/alliances")
def alliance_listing():
    import screeps_loan.models.alliances as alliances
    import screeps_loan.models.users as users

    alliance_query = alliances.AllianceQuery()
    all_alliances = alliance_query.getAll()
    alliances_id = [item["id"] for item in all_alliances]
    users_with_alliance = users.UserQuery().find_name_by_alliances(alliances_id)
    display_alliances = []
    for alliance in all_alliances:
        if not alliance["id"]:
            continue

        if alliances_model.get_room_count(alliance["id"]) < 2:
            continue

        alliance["users"] = [
            user
            for user in users_with_alliance
            if user["alliance_id"] == alliance["id"]
        ]
        if alliance["users"]:
            display_alliances.append(alliance)
    display_alliances = sorted(display_alliances, key=lambda k: k["fullname"])
    return render_template("alliance_listing.html", alliances=display_alliances)


@app.route("/a/<shortname>")
def alliance_profile(shortname):
    alliance = alliances_model.find_by_shortname(shortname)
    if alliance is None:
        return show_error(404, f'No alliance named "{shortname}" exists')

    from markdown2 import Markdown

    markdowner = Markdown()
    if "charter" not in alliance or alliance["charter"] is None:
        alliance["charter"] = "We don't have a charter yet."
    charter = markdowner.convert(alliance["charter"])
    # To sanitize and prevent XSS attack. To be decide if this will be too slow
    from lxml.html.clean import clean_html

    charter = clean_html(charter)
    alliance_url = "/a/%s.json" % (shortname)
    alliance_url = "/alliances.js"
    
    users = users_model.find_users_by_alliance(alliance['id'])

    maxroomshard0 = get_shard_size('shard0')
    maxroomshard1 = get_shard_size('shard1')
    maxroomshard2 = get_shard_size('shard2')
    maxroomshard3 = get_shard_size('shard3')


    return render_template(
        "alliance_profile.html", shortname=shortname, charter=charter, alliance=alliance, users=users, maxroomshard0=maxroomshard0, maxroomshard1=maxroomshard1, maxroomshard2=maxroomshard2,maxroomshard3=maxroomshard3
    )


@app.route("/a/<shortname>.json")
@cross_origin(origins="*", send_wildcard=True, methods="GET")
@httpresponse(expires=300, content_type="application/json")
def alliance_profile_json(shortname):
    users = users_model.find_name_by_alliance(shortname)
    users_aux = {}
    for user in users:
        users_aux[user] = {"members": [user], "name": user, "abbreviation": user}

    return json.dumps(users_aux)


@app.route("/alliances/rankings")
def alliance_rankings():
    rankings = rankings_model.get_all_rankings()
    return render_template("alliance_rankings.html", rankings=rankings)


@app.route("/alliances/rankings/<ranking_type>.js")
@cross_origin(origins="*", send_wildcard=True, methods="GET")
@httpresponse(expires=300, content_type="application/json")
def alliance_rankings_json(ranking_type):
    rankings = rankings_model.get_rankings_by_import_and_type(ranking_type)
    return json.dumps(rankings)

@cache.cache()
def get_shard_size(shard):
    api = get_client()
    api_worldsize = api.worldsize(shard)
    return int((api_worldsize["width"] - 2) / 2)