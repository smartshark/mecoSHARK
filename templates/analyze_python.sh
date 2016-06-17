#!/bin/sh
cd $results
$pythonSourcemeter -projectBaseDir:$input -projectName:$projectname -resultsDir:$results -runMetricHunter=false -runFaultHunter=false -runPylint=false -runDCF=true
