#!/bin/sh

PLUGIN_PATH=$1
REPOSITORY_PATH=$2
NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

cp -R $REPOSITORY_PATH "/dev/shm/$NEW_UUID"

cd "/dev/shm/$NEW_UUID"
git checkout $3 --quiet

export PATH=$PATH:$PLUGIN_PATH/external/sloccount2.26

COMMAND="python3.5 $PLUGIN_PATH/main.py --input /dev/shm/$NEW_UUID --output /dev/shm/$NEW_UUID --rev $3 --url $4 --db-hostname $5 --db-port $6 --db-database $7"

if [ ! -z ${8+x} ]; then
	COMMAND="$COMMAND --db-user ${8}"
fi

if [ ! -z ${9+x} ]; then
	COMMAND="$COMMAND --db-password ${9}"
fi

if [ ! -z ${10+x} ]; then
	COMMAND="$COMMAND --db-authentication ${10}"
fi

if [ ! -z ${11+x} ]; then
	COMMAND="$COMMAND --options ${11}"
fi

$COMMAND

rm -rf "/dev/shm/$NEW_UUID"