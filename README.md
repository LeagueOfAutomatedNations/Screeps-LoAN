# Requirements
- Postgres
- Python 3.x

# Setup

Update the info in settings.example

```
pip install -r requirements.txt
export SETTINGS=/path//to/settings
export FLASK_APP=screeps_loan/screeps_loan.py
python db/manage.py version_control
python db/manage.py upgrade
flask run
flask import_users  #This actually will run map stats to get all users on the map
flask import_alliances #Importing alliance from alliances.js file
```

# Testing with Vagrant

1. Install vagrant.
2. Copy `provisioning/settings` to project root and add your screeps api credentials.
3. Run `vagrant up` in the project root.
4. Wait.
5. Once complete open http://127.0.0.1:8080/ in a browser.
