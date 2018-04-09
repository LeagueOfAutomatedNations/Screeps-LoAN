from screeps_loan.models import db
from screeps_loan.services.cache import cache
from screeps_loan.models.db import get_conn

class UserQuery():
    def find_name_by_alliances(self, alliances):
        query = "SELECT ign, alliance FROM users where alliance = ANY(%s)"
        result = db.find_all(query, (alliances,))
        return [{"name": row[0], "alliance": row[1]} for row in result]

    def update_alliance_by_screeps_id(self, id, alliance):
        query = "UPDATE users SET alliance = %s WHERE screeps_id=%s"
        db.execute(query, (alliance, id))


def find_name_by_alliance(alliance):
    query = "SELECT ign FROM users where alliance = %s"
    result = db.find_all(query, (alliance,))
    return [row[0] for row in result]


def update_alliance_by_screeps_id(id, alliance):
    query = "UPDATE users SET alliance = %s WHERE screeps_id=%s"
    db.execute(query, (alliance, id))


def update_alliance_by_user_id(id, alliance):
    query = "UPDATE users SET alliance = %s WHERE id=%s"
    db.execute(query, (alliance, id))


def update_gcl_by_user_id(id, gcl):
    query = "UPDATE users SET gcl = %s WHERE id=%s"
    db.execute(query, (gcl, id))


def update_power_by_user_id(id, power):
    query = "UPDATE users SET power = %s WHERE id=%s"
    db.execute(query, (power, id))


@cache.cache(expire=60)
def get_all_users():
    query = "SELECT * FROM users"
    return db.find_all(query)


@cache.cache()
def player_id_from_db(name):
    query = "SELECT screeps_id FROM users WHERE LOWER(ign)=LOWER(%s)"
    row = db.find_one(query, (name,))
    if (row is not None):
        return row[0]
    return None


@cache.cache()
def user_id_from_db(name):
    query = "SELECT id FROM users WHERE LOWER(ign)=LOWER(%s)"
    row = db.find_one(query, (name,))
    if (row is not None):
        return row[0]
    return None


@cache.cache()
def user_name_from_db_id(id):
    query = "SELECT ign FROM users WHERE id=%s"
    row = db.find_one(query, (id,))
    if (row is not None):
        return row[0]
    return None


@cache.cache()
def get_player_room_count(player):
    query = '''
    SELECT COUNT(DISTINCT rooms.name)
          FROM rooms,users
          WHERE rooms.owner=users.id
              AND users.ign=%s
              AND rooms.import = (SELECT id
                                      FROM room_imports
                                      ORDER BY id desc
                                      LIMIT 1
                                  );
    '''
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(query, (player,))
    result = cursor.fetchone()
    return int(result[0])



def insert_username_with_id(name, id):
    query = "INSERT INTO users(ign, screeps_id) VALUES(%s, %s)"
    conn = db.get_conn()
    cursor = conn.cursor()
    cursor.execute(query, (name, id))
    conn.commit()


def alliance_of_user(id):
    query = '''SELECT fullname, shortname, logo, charter, slack_channel, color
                from users JOIN alliances ON alliance=shortname where id=%s'''
    return db.find_one(query, (id,))
