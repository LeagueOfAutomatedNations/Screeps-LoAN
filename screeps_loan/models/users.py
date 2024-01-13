from screeps_loan.models import db
from screeps_loan import app
from screeps_loan.services.cache import cache
from screeps_loan.models.db import get_conn


class UserQuery:
    def find_name_by_alliances(self, alliances):
        query = "SELECT ign, alliance_id FROM users where alliance_id = ANY(%s)"
        result = db.find_all(query, (alliances,))
        return [{"name": row[0], "alliance_id": row[1]} for row in result]

    def update_alliance_by_screeps_id(self, id, alliance_id):
        query = "UPDATE users SET alliance_id = %s WHERE screeps_id=%s"
        db.execute(query, (alliance_id, id))


def find_name_by_alliance(alliance_id):
    query = "SELECT ign FROM users where alliance_id = %s"
    result = db.find_all(query, (alliance_id,))
    return [row[0] for row in result]

def find_users_by_alliance(alliance_id):
    query = "SELECT ign, combined_rcl, spawncount, gcl_level FROM users where alliance_id = %s"
    result = db.find_all(query, (alliance_id,))
    return [{"ign":row[0], "combined_rcl":row[1],"spawn_count":row[2],"gcl_level":row[3]} for row in result]


def update_alliance_by_screeps_id(id, alliance_id):
    query = "UPDATE users SET alliance_id = %s WHERE screeps_id=%s"
    db.execute(query, (alliance_id, id))


def update_alliance_by_user_id(user_id, alliance_id, isKicked=False):
    conn = db.get_conn()
    try:
        query = "UPDATE users SET alliance_id = %s WHERE id=%s"
        cursor = conn.cursor()
        cursor.execute(query, (None if isKicked else alliance_id, user_id))

        query = "INSERT INTO alliance_history(alliance_FK, user_FK, change_type, change) VALUES(%s, %s, %s, %s)"
        cursor.execute(query, (alliance_id, user_id, "joined" if alliance_id != None else "kicked", ""))

        conn.commit()
    except Exception as e:
        conn.rollback()


def update_gcl_by_user_id(id, gcl):
    query = "UPDATE users SET gcl = %s WHERE id=%s"
    db.execute(query, (gcl, id))


def update_power_by_user_id(id, power):
    query = "UPDATE users SET power = %s WHERE id=%s"
    db.execute(query, (power, id))


def update_gcl_level_by_user_id(id, gcl_level):
    query = "UPDATE users SET gcl_level = %s WHERE id=%s"
    db.execute(query, (gcl_level, id))


def update_combined_rcl_by_user_id(id, combined_rcl):
    query = "UPDATE users SET combined_rcl = %s WHERE id=%s"
    db.execute(query, (combined_rcl, id))


def update_spawncount_by_user_id(id, spawncount):
    query = "UPDATE users SET spawncount = %s WHERE id=%s"
    db.execute(query, (spawncount, id))


@cache.cache(expire=60)
def get_all_users():
    query = "SELECT * FROM users"
    return db.find_all(query)


def get_all_users_for_importing():
    query = "SELECT * FROM users ORDER BY gcl IS NOT NULL, RANDOM()"
    return db.find_all(query)


@cache.cache()
def player_id_from_db(name):
    query = "SELECT screeps_id FROM users WHERE LOWER(ign)=LOWER(%s)"
    row = db.find_one(query, (name,))
    if row is not None:
        return row[0]
    return None


@cache.cache()
def user_id_from_db(name):
    query = "SELECT id FROM users WHERE LOWER(ign)=LOWER(%s)"
    row = db.find_one(query, (name,))
    if row is not None:
        return row[0]
    return None


@cache.cache()
def user_name_from_db_id(id):
    query = "SELECT ign FROM users WHERE id=%s"
    row = db.find_one(query, (id,))
    if row is not None:
        return row[0]
    return None

@cache.cache()
def get_player_room_count(player):
    query = """
    SELECT COUNT(DISTINCT rooms.name)
          FROM rooms,users
          WHERE rooms.owner=users.id
              AND users.ign=%s
              AND rooms.import = (SELECT id
                                      FROM room_imports
                                      ORDER BY id desc
                                      LIMIT 1
                                  );
    """
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


def alliance_of_user(user_id):
    query = """SELECT *
                FROM alliances
                WHERE id = (SELECT alliance_id FROM users WHERE id = %s LIMIT 1);"""
    return db.find_one(query, (user_id,))


def getUserRCL(user):
    query = "SELECT id FROM room_imports WHERE status LIKE 'complete' ORDER BY started_at DESC"
    result = db.find_one(query)
    room_import_id = result[0]

    query = "SELECT SUM(level) FROM rooms WHERE rooms.owner = %s AND rooms.import=%s"
    conn = db.get_conn()
    cursor = conn.cursor()
    cursor.execute(query, (user, room_import_id))
    result = cursor.fetchone()[0]
    if result is not None:
        return result
    return 0


def convertGcl(control):
    return int((control / 1000000) ** (1 / 2.4)) + 1


def getUserSpawns(user):
    query = "SELECT id FROM room_imports WHERE status LIKE 'complete' ORDER BY started_at DESC"
    result = db.find_one(query)
    room_import_id = result[0]

    count = 0
    query = "SELECT COUNT(*) FROM rooms WHERE rooms.owner = %s AND level>=8 AND rooms.import=%s"
    conn = db.get_conn()
    cursor = conn.cursor()
    cursor.execute(query, (user, room_import_id))
    result = cursor.fetchone()[0]
    if result is not None:
        if result:
            count += result * 3

    query = "SELECT COUNT(*) FROM rooms WHERE rooms.owner = %s AND level=7 AND rooms.import=%s"
    cursor = conn.cursor()
    cursor.execute(query, (user, room_import_id))
    result = cursor.fetchone()[0]
    if result is not None:
        if result:
            count += result * 2

    query = "SELECT COUNT(*) FROM rooms WHERE rooms.owner = %s AND level>=1 AND level<7 AND rooms.import=%s"
    cursor = conn.cursor()
    cursor.execute(query, (user, room_import_id))
    result = cursor.fetchone()[0]
    if result is not None:
        if result:
            count += result

    return count
