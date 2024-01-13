from screeps_loan.models import db
from screeps_loan.services.cache import cache


def add_or_update_invite(user_id, alliance_id, sender):
    conn = db.get_conn()
    try:
        # Delete existing invite
        delete_query = "DELETE FROM alliance_invites WHERE alliance_id = %s AND user_id = %s"
        delete_cursor = conn.cursor()
        delete_cursor.execute(delete_query, (alliance_id, user_id))
        conn.commit()

        # Insert new invite with updated timestamp
        insert_query = (
            "INSERT INTO alliance_invites(alliance_id, user_id, sender) "
            "VALUES (%s, %s, %s)"
        )
        insert_cursor = conn.cursor()
        insert_cursor.execute(insert_query, (alliance_id, user_id, sender))
        conn.commit()
    except Exception as e:
        conn.rollback()


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
