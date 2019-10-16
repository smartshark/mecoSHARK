#!/bin/sh
cd $results
$javaSourcemeter -maximumThreads=4 -projectName=$projectname -buildScript=build-maven.sh -resultsDir=$results -runMetricHunter=false -runDCF=true -runFB=false -runPMD=true
