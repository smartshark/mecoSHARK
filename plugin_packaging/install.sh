#!/bin/sh
PLUGIN_PATH=$1

cd $PLUGIN_PATH/external/sloccount2.26
make

# cd $PLUGIN_PATH/external/sourcemeter/Java
# ./installMavenWrapper.sh

cd $PLUGIN_PATH/external
wget --quiet https://github.com/smartshark/OpenStaticAnalyzer/releases/download/v4.0.0-smartshark/OpenStaticAnalyzer-4.0.0-x64-Linux.tgz
tar -xvf OpenStaticAnalyzer-4.0.0-x64-Linux.tgz
mv OpenStaticAnalyzer-4.0.0-x64-Linux openStaticAnalyzer

cd $PLUGIN_PATH

# Install testimpshark
python3.5 $PLUGIN_PATH/setup.py install --user
