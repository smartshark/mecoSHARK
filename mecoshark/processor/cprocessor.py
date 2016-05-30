import logging
import os
import shutil
import subprocess

from mecoshark.processor.baseprocessor import BaseProcessor
from mecoshark.resultparser.sourcemetercparser import SourcemeterCParser
from mecoshark.resultparser.sourcemeterparser import SourcemeterParser


class CProcessor(BaseProcessor):
    @property
    def supported_languages(self):
        return ['ansic', 'cpp', 'cs', 'c']

    @property
    def enabled(self):
        return True

    @property
    def threshold(self):
        return 0.4

    def __init__(self, output_path, input_path):
        super().__init__(output_path, input_path)
        self.logger = logging.getLogger("processor")
        return

    def execute_sourcemeter(self, options):
        # Clean output directory
        shutil.rmtree(os.path.join(self.output_path, self.projectname), True)
        template_path = os.path.dirname(os.path.realpath(__file__))+'/../../templates'

        self.logger.info("Trying out directory analysis for cpp/c/cs...")
        self.prepare_template(os.path.join(template_path, 'analyze_c.sh'))

        if 'makefile' in options:
            build_string = options['makefile']
        else:
            build_string = "#!/bin/sh\ncd $input\nmake distclean\n./configure\nmake"

        with open(os.path.join(template_path, 'build.sh'), 'w') as build_file:
            build_file.write(build_string)

        self.prepare_template(os.path.join(template_path, 'build.sh'))
        self.prepare_template(os.path.join(template_path, 'external-filter.txt'))
        subprocess.run(os.path.join(self.output_path, 'analyze_c.sh'), shell=True, cwd=self.input_path)

        if not self.is_output_produced():
            self.logger.error('Problem in using mecoshark! No output was produced!')

    def is_output_produced(self):

        output_path = os.path.join(self.output_path, self.projectname, 'cpp')

        if not os.path.exists(output_path):
            return False

        output_path = os.path.join(output_path, os.listdir(output_path)[0])

        number_of_files = len([name for name in os.listdir(output_path) if name.endswith('.csv')])

        if number_of_files == 14:
            return True

        return False

    def process(self, revision, url, options):
        self.execute_sourcemeter(options)
        output_path = os.path.join(self.output_path, self.projectname, 'cpp')
        output_path = os.path.join(output_path, os.listdir(output_path)[0])

        parser = SourcemeterCParser(output_path, self.input_path, url, revision)
        parser.store_data()
        parser.store_clone_data()



