import logging
import os
import shutil
import subprocess

import sys

from mecoshark.processor.baseprocessor import BaseProcessor
from mecoshark.resultparser.sourcemeterparser import SourcemeterParser


class JavaProcessor(BaseProcessor):
    @property
    def supported_languages(self):
        return ['java']

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

    def execute_sourcemeter(self):
        # Clean output directory
        shutil.rmtree(os.path.join(self.output_path, self.projectname), True)
        template_path = os.path.dirname(os.path.realpath(__file__))+'/../../templates'
        failure_happened = True

        '''
        # try maven
        if os.path.exists(os.path.join(self.input_path, 'pom.xml')):
            self.logger.info("Trying out maven...")
            self.prepare_template(os.path.join(template_path, 'build-maven.sh'))
            self.prepare_template(os.path.join(template_path, 'analyze-maven.sh'))

            try:
                subprocess.run(os.path.join(self.output_path, 'analyze-maven.sh'), shell=True)
            except Exception:
                sys.exit(1)
                pass

            if not self.is_output_produced():
                sys.exit(1)
                shutil.rmtree(os.path.join(self.output_path, self.projectname), True)
                failure_happened = True

        if os.path.exists(os.path.join(self.input_path, 'build.xml')) and failure_happened:
            self.logger.info("Trying out ant...")
            self.prepare_template(os.path.join(template_path, 'build-ant.sh'))
            self.prepare_template(os.path.join(template_path, 'analyze-ant.sh'))

            try:
                subprocess.run(os.path.join(self.output_path, 'analyze-ant.sh'), shell=True)
            except Exception:
                pass

            if not self.is_output_produced():
                shutil.rmtree(os.path.join(self.output_path, self.projectname), True)
                failure_happened = True
        '''

        if failure_happened:
            self.logger.info("Trying out directory analysis for java...")
            self.prepare_template(os.path.join(template_path, 'analyze-dir.sh'))

            if self.input_path.endswith("/"):
                self.input_path = self.input_path[:-1]

            if self.output_path.endswith("/"):
                self.output_path = self.output_path[:-1]

            try:
                subprocess.run(os.path.join(self.output_path, 'analyze-dir.sh'), shell=True)
            except Exception:
                pass

        if not self.is_output_produced():
            self.logger.error('Problem in using mecoshark! No output was produced!')

    def is_output_produced(self):

        output_path = os.path.join(self.output_path, self.projectname, 'java')

        if not os.path.exists(output_path):
            return False

        output_path = os.path.join(output_path, os.listdir(output_path)[0])

        number_of_files = len([name for name in os.listdir(output_path) if name.endswith('.csv')])

        if number_of_files == 12:
            return True

        return False

    def process(self, revision, url, options):
        self.execute_sourcemeter()

        output_path = os.path.join(self.output_path, self.projectname, 'java')
        output_path = os.path.join(output_path, os.listdir(output_path)[0])

        parser = SourcemeterParser(output_path, self.input_path, url, revision)
        parser.store_data()

        # delete directory
        shutil.rmtree(os.path.join(self.output_path, self.projectname), True)




