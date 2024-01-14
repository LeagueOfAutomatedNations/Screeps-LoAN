from screeps_loan.models import db
from screeps_loan.services.cache import cache


class AllianceQuery:
    def getAll(self):
        query = "SELECT shortname, fullname, discord_url, color, logo, id FROM alliances ORDER BY shortname"
        result = db.find_all(query)
        return [
            {
                "shortname": i[0],
                "fullname": i[1],
                "discord_url": i[2],
                "color": i[3],
                "logo": i[4],
                "id": i[5],
            }
            for i in result
        ]
    
    def getAllByShard(self, shard):
        query = """
SELECT alliances.shortname, alliances.fullname, alliances.discord_url, alliances.color, alliances.logo, alliances.id
FROM alliances
JOIN users ON alliances.id = users.alliance_id
JOIN rooms ON users.id = rooms.owner
WHERE users.alliance_id = alliances.id
    AND rooms.shard = %s
    AND rooms.import = (
        SELECT id
        FROM room_imports
        ORDER BY id DESC
        LIMIT 1
    )
GROUP BY alliances.shortname, alliances.fullname, alliances.discord_url, alliances.color, alliances.logo, alliances.id
HAVING COUNT(DISTINCT rooms.name) > 0
ORDER BY alliances.shortname;
        """
        result = db.find_all(query, (shard.replace('shard','')))
        return [
            {
                "shortname": i[0],
                "fullname": i[1],
                "discord_url": i[2],
                "color": i[3],
                "logo": i[4],
                "id": i[5],
            }
            for i in result
        ]

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
                      users.alliance_id = alliances.id
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
        return [
            {
                "shortname": row[0],
                "members": row[1].split(","),
                "active_member_count": int(row[2]),
                "room_count": int(row[3]),
            }
            for row in result
        ]

    def getMembershipDataByShard(self, shard):
        query = "SELECT id FROM room_imports ORDER BY id desc LIMIT 1"
        result = db.find_one(query)
        if result is None:
            return []
        import_id = result[0]

        query = """
SELECT
    t.alliance_id,
    string_agg(t.ign, ',') AS members,
    SUM(CASE WHEN t.room_count > 0 THEN 1 ELSE 0 END) AS active_member_count,
    SUM(t.room_count) AS room_count
FROM
    (
        SELECT
            COUNT(DISTINCT rooms.name) AS room_count,
            users.ign,
            users.alliance_id
        FROM
            users
        JOIN
            alliances
        ON
            users.alliance_id = alliances.id
        LEFT JOIN
            rooms
        ON
            rooms.owner = users.id
            AND rooms.import = %s
            AND rooms.shard = %s
        WHERE rooms.shard = %s
        GROUP BY
            users.ign,
            users.alliance_id
        ORDER BY
            users.ign
    ) t
GROUP BY
    t.alliance_id
HAVING SUM(t.room_count) > 0 -- Add this condition
ORDER BY
    t.alliance_id;
        """
        result = db.find_all(query, (import_id,shard.replace('shard',''),shard.replace('shard','')))
        return_value = []
        return [
            {
                "id": row[0],
                "members": row[1].split(","),
                "active_member_count": int(row[2]),
                "room_count": int(row[3]),
            }
            for row in result
        ]

    def find_by_shortname(self, name):
        query = "SELECT id from alliances where shortname=%s"
        result = db.find_one(query, (name,))
        if result is not None:
            return result[0]
        return None

    def find_by_id(self, alliance_id):
        query = "SELECT fullname from alliances where id=%s"
        result = db.find_one(query, (alliance_id,))
        if result is not None:
            return result[0]
        return None

    def insert_alliance(self, shortname, fullname, color="#000000", discord_url=None):
        conn = db.get_conn()
        try:
            query = """INSERT INTO alliances(shortname, fullname, color, discord_url) \
                     VALUES(%s, %s, %s, %s)"""
            cursor = conn.cursor()
            cursor.execute(query, (shortname, fullname, color, discord_url))
            alliance_id = cursor.fetchone()[0]

            conn.commit()
            return alliance_id
        except Exception as e:
            conn.rollback()

def update_logo_of_alliance(alliance_id, user_id, logo):
    conn = db.get_conn()
    try:
        query = "UPDATE alliances SET logo=%s WHERE id = %s"
        cursor = conn.cursor()
        cursor.execute(query, (logo, alliance_id))

        query = "INSERT INTO alliance_history(alliance_FK, user_FK, change_type, change) VALUES(%s, %s, %s, %s)"
        cursor.execute(query, (alliance_id, user_id, "logo", logo))

        conn.commit()
    except Exception as e:
        conn.rollback()


def update_charter_of_alliance(alliance_id, user_id, charter):
    conn = db.get_conn()
    try:
        query = "UPDATE alliances SET charter=%s WHERE id = %s"
        cursor = conn.cursor()
        cursor.execute(query, (charter, alliance_id))

        query = "INSERT INTO alliance_history(alliance_FK, user_FK, change_type, change) VALUES(%s, %s, %s, %s)"
        cursor.execute(query, (alliance_id, user_id,"charter", charter))

        conn.commit()
    except Exception as e:
        conn.rollback()


def update_all_alliances_info(
    alliance_id, user_id, new_shortname, fullname, discord_url, color="#000000"
):
    conn = db.get_conn()
    try:
        color = str(color)
        query = "UPDATE alliances SET color = %s, shortname = %s, fullname = %s, discord_url = %s WHERE id = %s"
        cursor = conn.cursor()
        cursor.execute(query, (color, new_shortname, fullname, discord_url, alliance_id))

        query = "INSERT INTO alliance_history(alliance_FK, user_FK, change_type, change) VALUES(%s, %s, %s, %s)"
        cursor.execute(query, (alliance_id, user_id, "all", "shortname: " + new_shortname + ", fullname: " + fullname + ", discord_url: " + discord_url + ", color: " + color))

        conn.commit()
    except Exception as e:
        conn.rollback()

def create_an_alliance(user_id, fullname, shortname, color="#000000"):
    conn = db.get_conn()
    try:
        query = "INSERT INTO alliances(fullname, shortname, color) VALUES(%s, %s, %s) returning Id"
        cursor = conn.cursor()
        cursor.execute(query, (fullname, shortname, color))
        alliance_id = cursor.fetchone()[0]

        query = "UPDATE users SET alliance_id = %s, alliance_role = 'owner' WHERE id = %s"
        cursor.execute(query, (alliance_id, user_id))

        query = "INSERT INTO alliance_history(alliance_FK, user_FK, change_type, change) VALUES(%s, %s, %s, %s)"
        cursor.execute(query, (alliance_id, user_id, "create", fullname))

        conn.commit()
    except Exception as e:
        conn.rollback()


def find_by_shortname(name):
    import psycopg2.extras

    conn = db.get_conn()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "SELECT * FROM alliances where shortname=%s"
    cursor.execute(query, (name,))
    result = cursor.fetchone()
    return result

@cache.cache()
def find_shortname_by_id(alliance_id):
    query = "SELECT shortname from alliances where id=%s"
    result = db.find_one(query, (alliance_id,))
    if result is not None:
        return result[0]
    return None

@cache.cache()
def get_room_count(alliance_id):
    query = """
    SELECT COUNT(DISTINCT rooms.name)
        FROM rooms,users
        WHERE rooms.owner=users.id
            AND users.alliance_id=%s
            AND rooms.import = (SELECT id
                                    FROM room_imports
                                    ORDER BY id desc
                                    LIMIT 1
                                );
    """
    result = db.find_one(query, (alliance_id,))
    return int(result[0])

@cache.cache()
def get_room_count_by_shard(alliance_id, shard):
    query = """
    
    """
    result = db.find_one(query, (alliance_id,shard))
    return int(result[0])