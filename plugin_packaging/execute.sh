#!/bin/sh

PLUGIN_PATH=$3
REPOSITORY_PATH=$2
NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

cp -R $REPOSITORY_PATH "/dev/shm/$NEW_UUID"

cd "/dev/shm/$NEW_UUID"
git checkout $1 >> /dev/null

export PATH=$PATH:$PLUGIN_PATH/external/sloccount2.26
python3.5 $PLUGIN_PATH/main.py --input "/dev/shm/$NEW_UUID" --output "/dev/shm/$NEW_UUID" --rev $1 --url $4 --db-user $5 --db-password $6 --db-database $7 --db-hostname $8 --db-port $9 --db-authentication ${10} --options ${11}

rm -rf "/dev/shm/$NEW_UUID"