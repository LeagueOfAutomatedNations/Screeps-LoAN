#!/usr/bin/env bash

cd /opt/screeps_loan

apt-get update
apt-get -f -y install git nano man
apt-get -f -y install nginx
apt-get -f -y install python3-pip python3-dev virtualenv
apt-get -f -y install postgresql postgresql-contrib libpq-dev

sudo -u postgres psql -c "CREATE USER screeps WITH PASSWORD 'screeps';"
sudo -u postgres psql -c "create database \"screeps\" with owner \"screeps\" encoding='utf8' template template0"

virtualenv -p /usr/bin/python3 env
source env/bin/activate
pip install -r requirements.txt
mkdir /home/screeps_loan/objects

export SETTINGS=/opt/screeps_loan/settings
export FLASK_APP=/opt/screeps_loan/screeps_loan/screeps_loan.py
python db/manage.py version_control
python db/manage.py upgrade
flask import_users  #This actually will run map stats to get all users on the map
flask import_alliances #Importing alliance from alliances.js file

rm /etc/nginx/sites-enabled/default
rm /etc/nginx/nginx.conf
ln -s /opt/screeps_loan/provisioning/etc/systemd/system/screeps_loan.service /etc/systemd/system/screeps_loan.service
ln -s /opt/screeps_loan/provisioning/etc/nginx/screeps_loan /etc/nginx/sites-enabled/screeps_loan
ln -s /opt/screeps_loan/provisioning/etc/nginx/nginx.conf /etc/nginx/nginx.conf

systemctl start screeps_loan.service
systemctl enable screeps_loan.service

systemctl restart nginx.service
systemctl enable nginx.service
