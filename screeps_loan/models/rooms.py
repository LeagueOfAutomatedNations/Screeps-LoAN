from screeps_loan.models import db

def get_all_rooms():
    query = "SELECT name, level, ign FROM rooms JOIN users ON rooms.owner = users.id"
    result = db.find_all(query)
    return [{'roomname': item[0], 'level': item[1], 'owner_name':item[2]} for item in result]

