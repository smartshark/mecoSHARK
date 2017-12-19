#!/bin/sh
cd $results
$pythonSourcemeter -maximumThreads:4 -externalHardFilter:external-filter-python.txt -projectBaseDir:$input -projectName:$projectname -resultsDir:$results -runMetricHunter=false -runFaultHunter=false -runPylint=true -runDCF=true
