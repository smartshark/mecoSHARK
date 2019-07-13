#!/bin/sh
$javaSourcemeter -maximumThreads=4 -projectName=$projectname -projectBaseDir=$input -resultsDir=$results -runMetricHunter=false -runDCF=true -runFB=false -runPMD=true
