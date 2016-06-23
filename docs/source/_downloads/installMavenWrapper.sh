#!/bin/bash
../maven3.2.5/bin/mvn install:install-file -Dfile=LinuxWrapper/WrapperBins/Tools/SourceMeter-Maven-plugin-mojo-executer-2.2.1.jar -DpomFile=LinuxWrapper/WrapperBins/Tools/SourceMeter-Maven-plugin-mojo-executer-2.2.1.pom
../maven3.2.5/bin/mvn install:install-file -Dfile=LinuxWrapper/WrapperBins/Tools/SourceMeter-Maven-plugin-mojo-executer-3.0.jar   -DpomFile=LinuxWrapper/WrapperBins/Tools/SourceMeter-Maven-plugin-mojo-executer-3.0.pom
../maven3.2.5/bin/mvn install:install-file -Dfile=LinuxWrapper/WrapperBins/Tools/SourceMeter-Maven-plugin-mojo-executer-3.1.jar   -DpomFile=LinuxWrapper/WrapperBins/Tools/SourceMeter-Maven-plugin-mojo-executer-3.1.pom

mavenVersionResult=`../maven3.2.5/bin/mvn -version | grep ^Apache* 2>/dev/null`

tokens=($mavenVersionResult)
ver_raw=${tokens[@]: 2:1} 
ver=${ver_raw:0:5}
mainver=${ver_raw:0:3}

echo "Current maven version is: $ver"

NOTTESTEDMSG="Warning! The maven wrapper has not been tested with the current maven version!"

if test "${mainver}" = "2.2" 
then
    if test "${ver}" != "2.2.1" 
    then 
        echo ${NOTTESTEDMSG}
    fi
    ../maven3.2.5/bin/mvn install:install-file -Dfile=LinuxWrapper/WrapperBins/Tools/SourceMeter-maven-plugin-8.0.jar -DpomFile=LinuxWrapper/WrapperBins/Tools/SourceMeter-maven-plugin-8.0-V2.pom
else if test "${mainver}" = "3.0" 
then
    if test "${ver}" != "3.0.5" 
    then 
        echo echo ${NOTTESTEDMSG}
    fi
    ../maven3.2.5/bin/mvn install:install-file -Dfile=LinuxWrapper/WrapperBins/Tools/SourceMeter-maven-plugin-8.0.jar -DpomFile=LinuxWrapper/WrapperBins/Tools/SourceMeter-maven-plugin-8.0-V3.pom
else if test "${mainver}" = "3.1" 
then
    if test "${ver}" != "3.1.1"  
    then 
        echo ${NOTTESTEDMSG}
    fi
    ../maven3.2.5/bin/mvn install:install-file -Dfile=LinuxWrapper/WrapperBins/Tools/SourceMeter-maven-plugin-8.0.jar -DpomFile=LinuxWrapper/WrapperBins/Tools/SourceMeter-maven-plugin-8.0-V31.pom
else if test "${mainver}" = "3.2" 
then
    if test "${ver}" != "3.2.2"  
    then 
        if test "${ver}" != "3.2.5"  
        then
            echo ${NOTTESTEDMSG}
        fi
    fi
    ../maven3.2.5/bin/mvn install:install-file -Dfile=LinuxWrapper/WrapperBins/Tools/SourceMeter-maven-plugin-8.0.jar -DpomFile=LinuxWrapper/WrapperBins/Tools/SourceMeter-maven-plugin-8.0-V31.pom
else
    echo "Error! Your maven version is not supported yet!"
    exit 1
fi
fi
fi
fi

../maven3.2.5/bin/mvn org.apache.maven.plugins:SourceMeter-maven-plugin:8.0:installyourself

echo "Maven plugin has been successfully installed."
exit 0