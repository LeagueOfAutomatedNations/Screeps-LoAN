from screeps_loan.models import db

class AllianceQuery():
    def getAll(self):
        query = "SELECT fullname, slack_channel FROM alliances"
        result = db.find_all(query)
        return [{"name": i[0], "slack_channel": i[1]} for i in result]


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
