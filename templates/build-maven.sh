#!/bin/sh
$mavenpath -f $mavenpom clean package -DskipTests -Dmaven.javadoc.skip=true -Dadditionalparam=-Xdoclint:none -T1C