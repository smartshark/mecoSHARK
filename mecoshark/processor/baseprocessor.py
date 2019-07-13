import abc
import os
import string
import stat

class BaseProcessor(metaclass=abc.ABCMeta):
    """ Main app for the mecoshark plugin

    :param output_path: path to an output directory, where files can be stored
    :param input_path: path to the revision that is used as input

    :property input_path: path to the revisionn that is used as input
    :property output_path: path to an output directory, where files can be stored
    :property projectname: name of the project (last part of input path)
    """
    @abc.abstractproperty
    def enabled(self):
        """
        Trigger to enable/disable plugins

        :return: boolean
        """
        return False

    @abc.abstractproperty
    def threshold(self):
        """
        Threshold on which the processor should be executed

        :example: If threshold is 0.4, then the processor is executed if more than 40% of all files have the supported file type.

        :return: threshold
        """
        return

    @abc.abstractproperty
    def supported_languages(self):
        """
        Currently: java, c, cs, cpp, python
        :return:
        """
        return

    def __init__(self, output_path, input_path):
        self.output_path = output_path
        self.input_path = input_path
        self.projectname = os.path.basename(os.path.normpath(input_path))

    @abc.abstractmethod
    def process(self, project_name, revision, url, options, debug_level):
        """
        Is called if a revision with hash "revision" should be processed.

        :param project_name: name of the project
        :param revision: revision_hash of the revision
        :param url: url of the project that is analyzed
        :param options: possible options (e.g. for CProcessor)
        :param debug_level: debugging_level
        :return:
        """
        return

    def prepare_template(self, template):
        """
        Copies the template from the template folder to the output_path and sets access rights.

        Several variables (marked with $<name>) are substituted, so that the template can be used right away

        :param template: path to the template
        :return:
        """
        sourcemeter_path = os.path.dirname(os.path.realpath(__file__))+'/../../external/openStaticAnalyzer/'
        java_sourcemeter = os.path.join(sourcemeter_path, 'Java/OpenStaticAnalyzerJava')
        python_sourcemeter = os.path.join(sourcemeter_path, 'Python/OpenStaticAnalyzerPython')
        c_sourcemeter = os.path.join(sourcemeter_path, 'CPP/SourceMeterCPP')
        maven_path = os.path.join(sourcemeter_path, 'maven3.2.5/bin/mvn')
        ant = os.path.join(sourcemeter_path, 'ant1.9.7/bin/ant')

        maven_pom = os.path.join(self.input_path, 'pom.xml')
        ant_build = os.path.join(self.input_path, 'build.xml')

        with open(template, 'r') as myTemplate:
            data = myTemplate.read()

        data_template = string.Template(data)
        out = data_template.safe_substitute(mavenpath=maven_path, mavenpom=maven_pom, antbuild=ant_build,
                                            javaSourcemeter=java_sourcemeter,
                                            results=self.output_path, projectname=self.projectname, input=self.input_path,
                                            pythonSourcemeter=python_sourcemeter,
                                            cSourcemeter=c_sourcemeter, ant=ant)

        output_path = os.path.join(self.output_path, os.path.basename(os.path.normpath(template)))
        with open(output_path, 'w') as myTemplate:
            myTemplate.write(out)

        st = os.stat(output_path)
        os.chmod(output_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
