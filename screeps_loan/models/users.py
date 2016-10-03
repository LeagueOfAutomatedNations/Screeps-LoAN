from screeps_loan.models import db

class UserQuery():
    def find_name_by_alliances(self, alliances):
        query = "SELECT ign, alliance FROM users where alliance = ANY(%s)"
        result = db.find_all(query, (alliances,))
        return [{"name": row[0], "alliance": row[1]} for row in result]

    def update_alliance_by_screeps_id (self, id, alliance):
        query = "UPDATE users SET alliance = %s WHERE screeps_id=%s"
        db.execute(query, (alliance, id))

def find_name_by_alliance(alliance):
    query = "SELECT ign FROM users where alliance = %s"
    result = db.find_all(query, (alliance,))
    return [row[0] for row in result]

def update_alliance_by_screeps_id (id, alliance):
    query = "UPDATE users SET alliance = %s WHERE screeps_id=%s"
    db.execute(query, (alliance, id))

def player_id_from_db(name):
    query = "SELECT screeps_id FROM users WHERE ign=%s"
    row = db.find_one(query, (name,))
    if (row is not None):
        return row[0]
    return None

def insert_username_with_id(name, id):
    query = "INSERT INTO users(ign, screeps_id) VALUES(%s, %s)"
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(query, (name, id))
    conn.commit()

def alliance_of_user(id):
    query = "SELECT fullname, shortname, logo, charter from users JOIN alliances ON alliance=shortname where id=%s"
    row = db.find_one(query, (id,))
    if (row is not None):
        return {'fullname': row[0], 'shortname': row[1], 'logo': row[2], 'charter': row[3]}
    return None
