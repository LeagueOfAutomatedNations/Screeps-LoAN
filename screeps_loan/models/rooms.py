from screeps_loan.models import db
from screeps_loan.services.cache import cache

def get_all_rooms(import_id=None):
    if not import_id:
        query = "SELECT id FROM room_imports WHERE status LIKE 'complete' ORDER BY started_at DESC"
        result = db.find_one(query)
        import_id = result[0]
    return get_rooms_by_import(import_id)


@cache.cache()
def get_rooms_by_import(import_id):
    query = "SELECT name, level, ign FROM rooms JOIN users ON rooms.owner = users.id WHERE import=(%s)"
    result = db.find_all(query, (import_id, ))
    return [{'roomname': item[0], 'level': item[1], 'owner_name':item[2]} for item in result]
