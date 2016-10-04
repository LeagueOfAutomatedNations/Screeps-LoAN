from screeps_loan.models import db

class AllianceQuery():
    def getAll(self):
        query = "SELECT shortname, fullname, slack_channel, color, logo FROM alliances"
        result = db.find_all(query)
        return [{"shortname":i[0], "fullname": i[1],
                 "slack_channel": i[2], "color": i[3], "logo": i[4]} for i in result]


    def find_by_shortname(self, name):
        query = "SELECT shortname from alliances where shortname=%s"
        result = db.find_one(query, (name,))
        if result is not None:
            return result[0]
        return None

    def insert_alliance(self, shortname, fullname, color, slack_channel = None):
        query = """INSERT INTO alliances(shortname, fullname, color, slack_channel) \
                 VALUES(%s, %s, %s, %s)"""
        result = db.execute(query, (shortname, fullname, color, slack_channel))

def update_logo_of_alliance(shortname, logo):
    query = "UPDATE alliances SET logo=%s WHERE shortname = %s"
    db.execute(query, (logo, shortname))


def update_charter_of_alliance(shortname, charter):
    query = "UPDATE alliances SET charter=%s WHERE shortname = %s"
    db.execute(query, (charter, shortname))


def update_all_alliances_info(shortname, new_shortname, fullname, slack_channel, color):
    color=str(color)
    query = "UPDATE alliances SET color = %s, shortname = %s, fullname = %s, slack_channel = %s WHERE shortname = %s"
    db.execute(query, (color, new_shortname, fullname, slack_channel, shortname))


def find_by_shortname(name):
    import psycopg2.extras

    conn = db.get_conn()
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
    query = "SELECT * FROM alliances where shortname=%s"
    cursor.execute(query, (name,))
    result = cursor.fetchone()
    return result

def create_an_alliance(user_id, fullname, shortname, color):
    conn = db.get_conn()
    try:
        query = "INSERT INTO alliances(fullname, shortname, color) VALUES(%s, %s, %s)"
        cursor = conn.cursor()
        cursor.execute (query, (fullname, shortname, color))

        query = "UPDATE users SET alliance = %s WHERE id = %s"
        cursor.execute(query, (shortname, user_id))

        conn.commit()
    except (e):
        conn.rollback()
