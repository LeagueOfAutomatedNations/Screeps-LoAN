from screeps_loan.models import db
from screeps_loan.services.cache import cache


def add_leader(alliance, user_id):
    query = "INSERT INTO alliances_leaders (alliance, user_id) VALUES (%s, %s)"
    db.execute(query, (alliance, user_id))

def remove_leader(alliance, user_id):
    query = "DELETE FROM alliances_leaders WHERE alliance= %s AND user_id= %s"
    db.execute(query, (alliance, user_id))

def get_leaders(alliance):
    query = "SELECT users.ign FROM alliances_leaders INNER JOIN users ON users.id = alliances_leaders.user_id WHERE alliances_leaders.alliance= %s"
    return db.find_all(query, (alliance,))
