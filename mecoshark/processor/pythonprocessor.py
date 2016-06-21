import logging
import os
import shutil
import subprocess

from mecoshark.processor.baseprocessor import BaseProcessor
from mecoshark.resultparser.sourcemeterparser import SourcemeterParser


class PythonProcessor(BaseProcessor):
    @property
    def supported_languages(self):
        return ['python']

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

        self.logger.info("Trying out directory analysis for python...")
        self.prepare_template(os.path.join(template_path, 'analyze_python.sh'))
        subprocess.run(os.path.join(self.output_path, 'analyze_python.sh'), shell=True)

        if not self.is_output_produced():
            self.logger.error('Problem in using mecoshark! No output was produced!')

    def is_output_produced(self):

        output_path = os.path.join(self.output_path, self.projectname, 'python')

        if not os.path.exists(output_path):
            return False

        output_path = os.path.join(output_path, os.listdir(output_path)[0])

        number_of_files = len([name for name in os.listdir(output_path) if name.endswith('.csv')])

        if number_of_files == 11:
            return True

        return False

    def process(self, revision, url, options):
        self.execute_sourcemeter()
        output_path = os.path.join(self.output_path, self.projectname, 'python')
        output_path = os.path.join(output_path, os.listdir(output_path)[0])

        parser = SourcemeterParser(output_path, self.input_path, url, revision)
        parser.store_data()

        shutil.rmtree(os.path.join(self.output_path, self.projectname), True)




