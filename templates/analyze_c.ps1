$dir = $pwd.Path
cd $results
& "$cSourcemeter" @("-maximumThreads=4", "-projectName=$projectname", "-buildScript=build.bat",  "-resultsDir=$results" , "-runCppcheck=true", "-runMetricHunter=false", "-runFaultHunter=false", "-runDCF=true", "-externalSoftFilter=external-filter.txt")
cd $dir