#!/bin/sh
$mavenpath -f $mavenpom clean package -DskipTests -Dadditionalparam=-Xdoclint:none -T1C