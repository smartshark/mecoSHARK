#!/bin/bash

current=`pwd`
rm -rf /tmp/mecoSHARK
mkdir -p /tmp/mecoSHARK/
cp -R ../mecoshark /tmp/mecoSHARK/
cp -R ../external /tmp/mecoSHARK
cp -R ../templates /tmp/mecoSHARK
cp ../setup.py /tmp/mecoSHARK
cp ../main.py /tmp/mecoSHARK
cp * /tmp/mecoSHARK/
cd /tmp/mecoSHARK/

tar -cvf "$current/mecoSHARK_plugin.tar" --exclude=*.tar --exclude=build_plugin.sh --exclude=*/tests --exclude=*/__pycache__ --exclude=*.pyc *
