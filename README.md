# Requirements
- Postgres
- Python 3.x

# Setup

Update the info in settings.example
``` pip install -r requirements.txt
export SETTINGS=/path//to/settings
export FLASK_APP=screeps_loan/screeps_loan.py
python db/manage.py version_control
python db/manage.py upgrade
flask run
flask import_users  #This actually will run map stats to get all users on the map
flask import_alliances #Importing alliance from alliances.js file
```