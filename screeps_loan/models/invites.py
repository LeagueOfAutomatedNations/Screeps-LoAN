from screeps_loan.models import db
from screeps_loan.services.cache import cache


def add_invite(user_id, alliance_id, sender):
    query = (
        "INSERT INTO alliance_invites(alliance_id, user_id, sender) VALUES (%s, %s, %s)"
    )
    db.execute(query, (alliance_id, user_id, sender))


def get_invites_by_user(user):
    query = "SELECT * FROM alliance_invites WHERE user_id=(%s)"
    return db.find_all(query, (user,))


def get_invites_by_alliance(alliance_id):
    query = "SELECT * FROM alliance_invites WHERE alliance_id=(%s)"
    return db.find_all(query, (alliance_id,))


def get_invite_by_id(id):
    query = "SELECT * from alliance_invites where id=%s"
    result = db.find_one(query, (id,))
    if result is not None:
        return result
    return None


def del_invites_by_user(user):
    query = "DELETE FROM alliance_invites WHERE user_id=(%s)"
    conn = db.get_conn()
    cursor = conn.cursor()
    return cursor.execute(query, (user,))


def del_invites_by_alliance(alliance_id):
    query = "DELETE FROM alliance_invites WHERE alliance_id=(%s)"
    conn = db.get_conn()
    cursor = conn.cursor()
    return cursor.execute(query, (alliance_id,))


def del_invite_by_id(id):
    query = "DELETE FROM alliance_invites WHERE id=(%s)"
    conn = db.get_conn()
    cursor = conn.cursor()
    return cursor.execute(query, (id,))
