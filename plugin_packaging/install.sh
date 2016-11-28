#!/bin/sh
PLUGIN_PATH=$1

cd $PLUGIN_PATH/external/sloccount2.26
make

cd $PLUGIN_PATH/external/sourcemeter/Java
./installMavenWrapper.sh

cd $PLUGIN_PATH

export PATH=$PATH:$PLUGIN_PATH/external/sloccount2.26

# Install testimpshark
python3.5 $PLUGIN_PATH/setup.py install --user