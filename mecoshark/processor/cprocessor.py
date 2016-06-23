import logging
import os
import shutil
import subprocess

from mecoshark.processor.baseprocessor import BaseProcessor
from mecoshark.resultparser.sourcemeterparser import SourcemeterParser


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
        return 0.4

    def __init__(self, output_path, input_path):
        super().__init__(output_path, input_path)
        self.logger = logging.getLogger("processor")
        return

    def execute_sourcemeter(self, options):
        """
        Executes sourcemeter with the given options

        :param options: options for execution (dictionary)
        """
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
        """
        Checks if output was produced for the process

        :return: boolean
        """

        output_path = os.path.join(self.output_path, self.projectname, 'cpp')

        if not os.path.exists(output_path):
            return False

        output_path = os.path.join(output_path, os.listdir(output_path)[0])

        number_of_files = len([name for name in os.listdir(output_path) if name.endswith('.csv')])

        if number_of_files == 14:
            return True

        return False

    def process(self, revision, url, options):
        """
        See: :func:`~mecoshark.processor.baseprocessor.BaseProcessor.process`

        Processes the given revision.
        First executes sourcemeter with given options, then it creates the parser to store the data.

        :param revision: revision
        :param url: url of the project that is analyzed
        :param options: options for execution
        """
        self.execute_sourcemeter(options)
        output_path = os.path.join(self.output_path, self.projectname, 'cpp')
        output_path = os.path.join(output_path, os.listdir(output_path)[0])

        parser = SourcemeterParser(output_path, self.input_path, url, revision)
        parser.store_data()

        shutil.rmtree(os.path.join(self.output_path, self.projectname), True)



