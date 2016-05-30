#!/bin/sh
cd $results
$cSourcemeter -projectName=$projectname -buildScript=build.sh -resultsDir=$results -runCppcheck=false -runMetricHunter=false -runFaultHunter=false -runDCF=true -externalSoftFilter=external-filter.txt