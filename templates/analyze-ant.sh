#!/bin/sh
cd $results
$javaSourcemeter -maximumThreads=4 -projectName=$projectname -buildScript=build-ant.sh -resultsDir=$results -runAndroidHunter=false -runMetricHunter=false -runVulnerabilityHunter=false -runFaultHunter=false -runDCF=true -runFB=false -runPMD=true