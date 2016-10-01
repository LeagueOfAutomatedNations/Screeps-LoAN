from screeps_loan.models import db

class Alliance(object):
    def __init__(self, row):
        self.name = row[0]
        self.slack_channel = row[1]

class AllianceQuery():
    def getAll(self):
        query = "SELECT name, slack_channel FROM alliances"
        result = db.find_all(query)
        return [{"name": i[0], "slack_channel": i[1]} for i in result]

