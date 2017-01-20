from screeps_loan.models import db
from screeps_loan.services.cache import cache

def get_all_rankings(import_id=None):
    if not import_id:
        query = "SELECT id FROM rankings_imports WHERE status LIKE 'complete' ORDER BY started_at DESC"
        result = db.find_one(query)
        import_id = result[0]
    return get_all_rankings_by_import(import_id)



def get_all_rankings_by_import(import_id):
    query = "SELECT * FROM rankings WHERE import=(%s) ORDER BY alliance_gcl DESC"
    return db.find_all(query, (import_id, ))
