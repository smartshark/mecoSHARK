#!/bin/sh

PLUGIN_PATH=$1
REPOSITORY_PATH=$2
NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

cp -R $REPOSITORY_PATH "/dev/shm/$NEW_UUID" || exit 1

cd "/dev/shm/$NEW_UUID" || exit 1
git checkout -f --quiet $3 || exit 1

COMMAND="python3.5 $PLUGIN_PATH/main.py --input /dev/shm/$NEW_UUID --output /dev/shm/$NEW_UUID --rev $3 --url $4 --project_name $5 --db-hostname $6 --db-port $7 --db-database $8"

if [ ! -z ${9+x} ] && [ ${9} != "None" ]; then
	COMMAND="$COMMAND --db-user ${9}"
fi

if [ ! -z ${10+x} ] && [ ${10} != "None" ]; then
	COMMAND="$COMMAND --db-password ${10}"
fi

if [ ! -z ${11+x} ] && [ ${11} != "None" ]; then
	COMMAND="$COMMAND --db-authentication ${11}"
fi

if [ ! -z "${12+x}" ] && [ "${12}" != "None" ]; then
	COMMAND="$COMMAND --makefile-contents \"${12}\""
fi

if [ ! -z ${13+x} ] && [ ${13} != "None" ]; then
	COMMAND="$COMMAND --debug ${12}"
fi

if [ ! -z ${14+x} ] && [ ${14} != "None" ]; then
	COMMAND="$COMMAND --ssl"
fi

export PATH=$PATH:$PLUGIN_PATH/external/sloccount2.26

eval $COMMAND

# if folder does not exist exit with 1
if [ ! -d "/dev/shm/$NEW_UUID/.git" ]; then
    (>&2 echo ".git folder not found!")
fi

# we still want cleanup
rm -rf "/dev/shm/$NEW_UUID"