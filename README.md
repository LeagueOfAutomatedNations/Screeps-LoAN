# Requirements

- Postgres
- Python 3.x

# Setup

Update the info in settings.example

```bash
cp settings.example settings
nano settings # add api settings.
pip install -r requirements.txt
export SETTINGS="`pwd`/settings"
export FLASK_APP=screeps_loan/screeps_loan.py
python db/manage.py version_control
python db/manage.py upgrade
flask run
flask import-users  #This actually will run map stats to get all users on the map
flask import-alliances #Importing alliance from alliances.js file
```

# Update Data

Bash wrapper scripts are provided to make updating easier.

```bash
./bin/import_users
./bin/import_alliances
```

# Testing with Vagrant

1. Install vagrant.
2. Copy `provisioning/settings` to project root and add your screeps api credentials.
3. Run `vagrant up` in the project root.
4. Wait.
5. Once complete open http://127.0.0.1:8080/ in a browser.
