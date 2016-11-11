#!/bin/sh
export GCONV_PATH=/usr/lib32/gconv
cd $input
make clean
export SM_DISABLE_ANALYSIS=true
./configure
unset SM_DISABLE_ANALYSIS
make