#!/bin/sh
cd $results
$javaSourcemeter -projectName=$projectname -buildScript=build-maven.sh -resultsDir=$results -runAndroidHunter=false -runMetricHunter=false -runVulnerabilityHunter=false -runFaultHunter=false -runDCF=true -runFB=false -runPMD=false
