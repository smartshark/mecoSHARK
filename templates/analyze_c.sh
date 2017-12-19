#!/bin/sh
cd $results
$cSourcemeter -maximumThreads=4 -projectName=$projectname -buildScript=build.sh -resultsDir=$results -runCppcheck=true -runMetricHunter=false -runFaultHunter=false -runDCF=true -externalSoftFilter=external-filter.txt