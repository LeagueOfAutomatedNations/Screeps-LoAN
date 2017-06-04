from screeps_loan import app
import screeps_loan.models.alliances as alliances_model
import screeps_loan.models.rankings as rankings_model
from screeps_loan.models.rooms import get_all_rooms
import screeps_loan.models.users as users_model
from screeps_loan.routes.decorators import httpresponse
import json
from flask import render_template
from flask_cors import cross_origin


@app.route('/alliances.js')
@cross_origin(origins="*", send_wildcard=True, methods="GET")
@httpresponse(expires=300, content_type='application/json')
def alliance_listing_json():
    import screeps_loan.models.alliances as alliances
    import screeps_loan.models.users as users

    alliance_query = alliances.AllianceQuery()
    all_alliances = alliance_query.getAll()
    alliances_name = [item["shortname"] for item in all_alliances]
    users_with_alliance = users.UserQuery().find_name_by_alliances(alliances_name)

    ranking_types = rankings_model.get_rankings_list()
    ranking_data = {}
    for ranking_type in ranking_types:
        ranking_data[ranking_type] = rankings_model.get_rankings_by_import_and_type(ranking_type)

    alliances_aux = {}
    for alliance in all_alliances:
        alliance['members'] = [user['name'] for user in users_with_alliance
                               if user['alliance'] == alliance['shortname']]


        filtered_members = [user for user in alliance['members'] if users_model.get_player_room_count(user) > 0]

        if len(filtered_members) < 2:
            continue

        if alliances_model.get_room_count(alliance['shortname']) < 2:
            continue

        alliances_aux[alliance['shortname']] = alliance
        alliance['name'] = alliance['fullname']
        alliance['abbreviation'] = alliance['shortname']
        alliance.pop('fullname', None)
        alliance.pop('shortname', None)

        for ranking_type in ranking_types:
            if alliance['abbreviation'] in ranking_data[ranking_type]:
                data = ranking_data[ranking_type][alliance['abbreviation']]
                alliance[ranking_type + '_rank'] = data

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
    return render_template("alliance_listing.html", alliances = display_alliances)


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
    alliance_url = '/a/%s.json' % (shortname)
    alliance_url = '/alliances.js'
    return render_template("alliance_profile.html", shortname = shortname, charter= charter, alliance=alliance);

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
