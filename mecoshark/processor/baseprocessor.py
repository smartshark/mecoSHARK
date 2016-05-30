import abc
import os
import string
import stat

class BaseProcessor(metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def enabled(self):
        return False

    @abc.abstractproperty
    def threshold(self):
        return

    @abc.abstractproperty
    def supported_languages(self):
        """
        Currently: java, c, cs, cpp, python, sh, etc.
        :return:
        """
        return

    def __init__(self, output_path, input_path):
        self.output_path = output_path
        self.input_path = input_path
        self.projectname = os.path.basename(os.path.normpath(input_path))

    @abc.abstractmethod
    def process(self, revision, url, options):
        return

    def prepare_template(self, template):
        sourcemeter_path = os.path.dirname(os.path.realpath(__file__))+'/../../external/sourcemeter/'
        java_sourcemeter = os.path.join(sourcemeter_path, 'Java/SourceMeterJava')
        python_sourcemeter = os.path.join(sourcemeter_path, 'Python/SourceMeterPython')
        c_sourcemeter = os.path.join(sourcemeter_path, 'CPP/SourceMeterCPP')
        maven_path = os.path.join(sourcemeter_path, 'maven3.2.5/bin/mvn')
        maven_pom = os.path.join(self.input_path, 'pom.xml')
        ant_build = os.path.join(self.input_path, 'build.xml')


        with open(template, 'r') as myTemplate:
            data = myTemplate.read()

        data_template = string.Template(data)
        out = data_template.safe_substitute(mavenpath=maven_path, mavenpom=maven_pom, antbuild=ant_build,
                                            javaSourcemeter=java_sourcemeter,
                                            results=self.output_path, projectname=self.projectname, input=self.input_path,
                                            pythonSourcemeter=python_sourcemeter,
                                            cSourcemeter=c_sourcemeter)

        output_path = os.path.join(self.output_path, os.path.basename(os.path.normpath(template)))
        with open(output_path, 'w') as myTemplate:
            myTemplate.write(out)

        st = os.stat(output_path)
        os.chmod(output_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)