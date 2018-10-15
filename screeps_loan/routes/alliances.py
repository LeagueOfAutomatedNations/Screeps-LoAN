import json

from flask import render_template
from flask_cors import cross_origin

import screeps_loan.models.alliances as alliances_model
import screeps_loan.models.rankings as rankings_model
import screeps_loan.models.users as users_model
from screeps_loan import app
from screeps_loan.routes.decorators import httpresponse


@app.route('/alliances.js')
@cross_origin(origins="*", send_wildcard=True, methods="GET")
@httpresponse(expires=300, content_type='application/json')
def alliance_listing_json():
    import screeps_loan.models.alliances as alliances

    alliance_query = alliances.AllianceQuery()
    all_alliances = alliance_query.getAll()

    alliance_users = alliance_query.getMembershipData()
    alliance_user_data = {}
    for users_row in alliance_users:
        alliance_user_data[users_row["shortname"]] = users_row

    ranking_types = rankings_model.get_rankings_list()
    ranking_data = {}
    for ranking_type in ranking_types:
        ranking_data[ranking_type] = rankings_model.get_rankings_by_import_and_type(ranking_type)

    alliances_aux = {}
    for alliance in all_alliances:
        if not alliance["shortname"] in alliance_user_data:
            continue

        if alliance_user_data[alliance["shortname"]]["active_member_count"] < 2:
            continue

        if alliance_user_data[alliance["shortname"]]["room_count"] < 2:
            continue

        alliance["members"] = alliance_user_data[alliance["shortname"]]["members"]
        alliance['name'] = alliance['fullname']
        alliance['abbreviation'] = alliance['shortname']
        alliance.pop('fullname', None)
        alliance.pop('shortname', None)

        for ranking_type in ranking_types:
            if alliance['abbreviation'] in ranking_data[ranking_type]:
                data = ranking_data[ranking_type][alliance['abbreviation']]
                alliance[ranking_type + '_rank'] = data
        alliances_aux[alliance['abbreviation']] = alliance

    return json.dumps(alliances_aux)


@app.route('/alliances')
def alliance_listing():
    import screeps_loan.models.alliances as alliances
    import screeps_loan.models.users as users

    alliance_query = alliances.AllianceQuery()
    all_alliances = alliance_query.getAll()
    alliances_name = [item["shortname"] for item in all_alliances]
    users_with_alliance = users.UserQuery().find_name_by_alliances(alliances_name)
    display_alliances = []
    for alliance in all_alliances:
        if not alliance['shortname']:
            continue

        if alliances_model.get_room_count(alliance['shortname']) < 2:
            continue

        alliance['users'] = [user for user in users_with_alliance if user['alliance'] == alliance['shortname']]
        if alliance['users']:
            display_alliances.append(alliance)
    display_alliances = sorted(display_alliances, key=lambda k: k['fullname'])
    return render_template("alliance_listing.html", alliances=display_alliances)


@app.route('/a/<shortname>')
def alliance_profile(shortname):
    alliance = alliances_model.find_by_shortname(shortname)
    from markdown2 import Markdown
    markdowner = Markdown()
    if "charter" not in alliance or alliance['charter'] is None:
        alliance['charter'] = "We don't have a charter yet."
    charter = markdowner.convert(alliance['charter'])
    # To sanitize and prevent XSS attack. To be decide if this will be too slow
    from lxml.html.clean import clean_html
    charter = clean_html(charter)
    return render_template("alliance_profile.html", shortname=shortname, charter=charter, alliance=alliance)


@app.route('/a/<shortname>.json')
@cross_origin(origins="*", send_wildcard=True, methods="GET")
@httpresponse(expires=300, content_type='application/json')
def alliance_profile_json(shortname):
    users = users_model.find_name_by_alliance(shortname)
    users_aux = {}
    for user in users:
        users_aux[user] = {"members": [user], "name": user, "abbreviation": user}

    return json.dumps(users_aux)


@app.route('/alliances/rankings')
def alliance_rankings():
    rankings = rankings_model.get_all_rankings()
    return render_template("alliance_rankings.html", rankings=rankings)


@app.route('/alliances/rankings/<ranking_type>.js')
@cross_origin(origins="*", send_wildcard=True, methods="GET")
@httpresponse(expires=300, content_type='application/json')
def alliance_rankings_json(ranking_type):
    rankings = rankings_model.get_rankings_by_import_and_type(ranking_type)
    return json.dumps(rankings)
