from screeps_loan.models import db
from screeps_loan.services.cache import cache

class AllianceQuery():
    def getAll(self):
        query = "SELECT shortname, fullname, slack_channel, color, logo FROM alliances ORDER BY shortname"
        result = db.find_all(query)
        return [{"shortname":i[0], "fullname": i[1],
                 "slack_channel": i[2], "color": i[3], "logo": i[4]} for i in result]

    def getMembershipData(self):
        query = "SELECT id FROM room_imports ORDER BY id desc LIMIT 1"
        result = db.find_one(query)
        if result is None:
            return []
        import_id = result[0]

        query = """
          SELECT
            t.alliance,
            string_agg(t.ign, ',') AS members,
            SUM(CASE WHEN t.room_count > 0 THEN 1 ELSE 0 END) AS active_member_count,
            SUM(t.room_count) AS room_count
            FROM
              (
                SELECT
                  COUNT(DISTINCT rooms.name) AS room_count,
                  users.ign,
                  users.alliance
                  FROM
                      users
                    JOIN
                      alliances
                    ON
                      users.alliance = alliances.shortname
                    LEFT JOIN
                      rooms
                    ON
                        rooms.owner = users.id
                      AND
                        rooms.import = %s
                  GROUP BY
                    users.ign,
                    users.alliance
                  ORDER BY
                    users.ign
            ) t
          GROUP BY
            t.alliance
          ORDER BY
            t.alliance;
        """
        result = db.find_all(query, (import_id,))
        return_value = []
        return [{"shortname": row[0], "members": row[1].split(","),
            "active_member_count": int(row[2]), "room_count": int(row[3])} for row in result]

    def find_by_shortname(self, name):
        query = "SELECT fullname from alliances where shortname=%s"
        result = db.find_one(query, (name,))
        if result is not None:
            return result[0]
        return None

    def insert_alliance(self, shortname, fullname, color = '#000000', slack_channel = None):
        query = """INSERT INTO alliances(shortname, fullname, color, slack_channel) \
                 VALUES(%s, %s, %s, %s)"""
        result = db.execute(query, (shortname, fullname, color, slack_channel))

def update_logo_of_alliance(shortname, logo):
    query = "UPDATE alliances SET logo=%s WHERE shortname = %s"
    db.execute(query, (logo, shortname))


def update_charter_of_alliance(shortname, charter):
    query = "UPDATE alliances SET charter=%s WHERE shortname = %s"
    db.execute(query, (charter, shortname))


def update_leader_of_alliance(shortname, leader_id):
    query = "UPDATE alliances SET leader=%s WHERE shortname = %s"
    db.execute(query, (leader_id, shortname))


def update_all_alliances_info(shortname, new_shortname, fullname, slack_channel, color='#000000'):
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


def create_an_alliance(user_id, fullname, shortname,  color='#000000'):
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


@cache.cache()
def get_room_count(shortname):
    query = '''
    SELECT COUNT(DISTINCT rooms.name)
        FROM rooms,users
        WHERE rooms.owner=users.id
            AND users.alliance=%s
            AND rooms.import = (SELECT id
                                    FROM room_imports
                                    ORDER BY id desc
                                    LIMIT 1
                                );
    '''
    result = db.find_one(query, (shortname,))
    return int(result[0])
