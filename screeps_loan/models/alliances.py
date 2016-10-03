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


def find_by_shortname(name):
    query = "SELECT * FROM alliances where shortname=%s"
    return db.find_one(query, (name,))
