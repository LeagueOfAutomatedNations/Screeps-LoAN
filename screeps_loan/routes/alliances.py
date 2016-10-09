from screeps_loan import app
import screeps_loan.models.alliances as alliances_model
from screeps_loan.models.rooms import get_all_rooms
import screeps_loan.models.users as users_model
import json
from flask import render_template


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


@app.route('/a/<shortname>')
def alliance_profile(shortname):

    room_data = get_all_rooms()
    room_data_aux = {}
    for room in room_data:
        room_data_aux[room['roomname']] = {'level': room['level'], 'owner': room['owner_name']}

    users = users_model.find_name_by_alliance(shortname)
    users_aux = {}
    for user in users:
        users_aux[user] = {"members": [user], "name": user, "abbreviation": user}

    alliance = alliances_model.find_by_shortname(shortname)
    from markdown2 import Markdown
    markdowner = Markdown()
    if (alliance['charter'] is None):
        alliance['charter'] = "We don't have a charter yet."
    charter = markdowner.convert(alliance['charter'])
    # To sanitize and prevent XSS attack. To be decide if this will be too slow
    from lxml.html.clean import clean_html
    charter = clean_html(charter)
    return render_template("alliance_profile.html", room_data = json.dumps(room_data_aux),
                           alliance_data = json.dumps(users_aux), charter= charter);
