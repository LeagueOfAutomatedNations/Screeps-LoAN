from screeps_loan.models import db
from screeps_loan.services.cache import cache


def get_rankings_list():
    return [
        "alliance_gcl",
        "combined_gcl",
        "average_gcl",
        "alliance_power",
        "combined_power",
        "rcl",
        "spawns",
        "members",
    ]


def get_all_rankings(import_id=None):
    if not import_id:
        query = "SELECT id FROM rankings_imports WHERE status LIKE 'complete' ORDER BY started_at DESC"
        result = db.find_one(query)
        import_id = result[0]
    return get_all_rankings_by_import(import_id)


def get_latest_import_id():
    query = "SELECT id FROM rankings_imports WHERE status LIKE 'complete' ORDER BY started_at DESC"
    result = db.find_one(query)
    if result is None:
        return None
    return result[0]


@cache.cache()
def get_all_rankings_by_import(import_id):
    query = "SELECT * FROM rankings WHERE import=(%s) ORDER BY alliance_gcl DESC"
    return db.find_all(query, (import_id,))


@cache.cache()
def get_rankings_by_import_and_type(ranking_type, import_id=None):
    allowed_types = get_rankings_list()
    if ranking_type not in allowed_types:
        raise ValueError("Not a valid ranking type")
    if not import_id:
        import_id = get_latest_import_id()

    query = (
        "SELECT alliance FROM rankings WHERE import=(%s) ORDER BY "
        + ranking_type
        + " DESC"
    )
    results = db.find_all(query, (import_id,))
    alliance_mapping = {}
    for index in range(len(results)):
        alliance_mapping[results[index][0]] = index + 1
    return alliance_mapping


@cache.cache()
def get_rankings_by_alliance_and_type(ranking_type, alliance_id, import_id=None):
    allowed_types = get_rankings_list()
    if ranking_type not in allowed_types:
        raise ValueError("Not a valid ranking type")

    if not import_id:
        import_id = get_latest_import_id()

    query = (
        "SELECT "
        + ranking_type
        + " FROM rankings WHERE alliance_id=(%s) AND import=(%s) ORDER BY "
        + ranking_type
        + " DESC"
    )
    return db.find_all(query, (alliance_id, import_id))
