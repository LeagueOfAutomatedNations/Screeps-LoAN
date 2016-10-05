#!/usr/bin/env bash

cd /vagrant

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
mkdir /home/ubuntu/objects

export SETTINGS=/vagrant/settings
export FLASK_APP=/vagrant/screeps_loan/screeps_loan.py
python db/manage.py version_control
python db/manage.py upgrade
flask import_users  #This actually will run map stats to get all users on the map
flask import_alliances #Importing alliance from alliances.js file




ln -s /vagrant/provisioning/screeps_loan.service /etc/systemd/system/screeps_loan.service
ln -s /vagrant/provisioning/nginx/screeps_loan /etc/nginx/sites-enabled/screeps_loan
rm /etc/nginx/sites-enabled/default


systemctl start screeps_loan.service
systemctl enable screeps_loan.service

systemctl restart nginx.service
systemctl enable nginx.service

