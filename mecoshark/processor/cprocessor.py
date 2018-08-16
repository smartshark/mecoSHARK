import logging
import os
import shutil
import subprocess

from mecoshark.utils import path_join, path_sanitize
from mecoshark.processor.baseprocessor import BaseProcessor
from mecoshark.resultparser.sourcemeterparser import SourcemeterParser

logger = logging.getLogger("processor")

class CProcessor(BaseProcessor):
    """
    Implements :class:`~mecoshark.processor.baseprocessor.BaseProcessor` for C-like languages
    """
    @property
    def supported_languages(self):
        """
        See: :func:`~mecoshark.processor.baseprocessor.BaseProcessor.supported_languages`
        """
        return ['ansic', 'cpp', 'cs', 'c']

    @property
    def enabled(self):
        """
        See: :func:`~mecoshark.processor.baseprocessor.BaseProcessor.enabled`
        """
        return True

    @property
    def threshold(self):
        """
        See: :func:`~mecoshark.processor.baseprocessor.BaseProcessor.threshold`
        """
        return 0.05

    def __init__(self, output_path, input_path):
        super().__init__(output_path, input_path)
        return

    def execute_sourcemeter(self, makefile_contents=None):
        """
        Executes sourcemeter with the given makefile_contents

        :param makefile_contents: makefile_contents for execution
        """
        # Clean output directory
        shutil.rmtree(path_join(self.output_path, self.projectname), True)
        template_path = path_sanitize(os.path.dirname(os.path.realpath(__file__))+'/../../templates')

        logger.info("Trying out directory analysis for cpp/c/cs...")

        if os.name == 'nt':
            template_filename = 'analyze_c.ps1'
            buildscript_name = 'build.bat'
        else:
            template_filename = 'analyze_c.sh'
            buildscript_name = 'build.sh'

        self.prepare_template(path_join(template_path, template_filename))

        if os.name != 'nt':
            build_string = '#!/bin/sh\n'
        else:
            build_string = ""
        if makefile_contents is not None:
            build_string += "cd $input\n"
            build_string += makefile_contents.replace("\\n", "\n")
        else:
            if os.name != 'nt':
                build_string += "cd $input\nmake distclean\n./configure\nmake"
            else:
                build_string += '& "msbuild" @("/t:Rebuild", "/p:Configuration=Release", "/p:Platform=Win32", "$projectname.sln")'

        with open(path_join(template_path, buildscript_name), 'w') as build_file:
            build_file.write(build_string)

        self.prepare_template(path_join(template_path, buildscript_name))
        self.prepare_template(path_join(template_path, 'external-filter.txt'))
        subprocess.run(path_join(self.output_path, template_filename), shell=True, cwd=self.input_path)

        if not self.is_output_produced():
            raise FileNotFoundError('Problem in using mecoshark! No output was produced!')

    def is_output_produced(self):
        """
        Checks if output was produced for the process

        :return: boolean
        """

        output_path = path_join(self.output_path, self.projectname, 'cpp')

        if not os.path.exists(output_path):
            return False

        output_path = path_join(output_path, os.listdir(output_path)[0])

        number_of_files = len([name for name in os.listdir(output_path) if name.endswith('.csv')])

        # Number of produced csv files must be 14.
        if number_of_files == 14:
            return True

        return False

    def process(self, revision, url, makefile_contents, debug_level):
        """
        See: :func:`~mecoshark.processor.baseprocessor.BaseProcessor.process`

        Processes the given revision.
        1) executes sourcemeter
        2) creates :class:`~mecoshark.resultparser.sourcemeterparser.SourcemeterParser` instance
        3) calls :func:`~mecoshark.resultparser.sourcemeterparser.SourcemeterParser.store_data`

        :param revision: revision
        :param url: url of the project that is analyzed
        :param makefile_contents: makefile_contents for execution
        :param debug_level: debugging_level
        """
        logger.setLevel(debug_level)
        self.execute_sourcemeter(makefile_contents)
        output_path = path_join(self.output_path, self.projectname, 'cpp')
        output_path = path_join(output_path, os.listdir(output_path)[0])

        parser = SourcemeterParser(output_path, self.input_path, url, revision, debug_level)
        parser.store_data()

        shutil.rmtree(path_join(self.output_path, self.projectname), True)
