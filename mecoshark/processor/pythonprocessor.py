import logging
import os
import shutil
import subprocess

from mecoshark.processor.baseprocessor import BaseProcessor
from mecoshark.resultparser.sourcemeterparser import SourcemeterParser

logger = logging.getLogger("processor")


class PythonProcessor(BaseProcessor):
    """
    Implements :class:`~mecoshark.processor.baseprocessor.BaseProcessor` for Python
    """
    @property
    def supported_languages(self):
        """
        See: :func:`~mecoshark.processor.baseprocessor.BaseProcessor.supported_languages`
        """
        return ['python']

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

    def execute_sourcemeter(self):
        """
        Executes sourcemeter for a python project
        """
        # Clean output directory
        shutil.rmtree(self.output_path, self.projectname, True)
        os.makedirs(self.output_path, exist_ok=True)
        template_path = os.path.dirname(os.path.realpath(__file__))+'/../../templates'

        logger.info("Trying out directory analysis for python...")
        self.prepare_template(os.path.join(template_path, 'analyze_python.sh'))
        self.prepare_template(os.path.join(template_path, 'external-filter-python.txt'))
        subprocess.run(os.path.join(self.output_path, 'analyze_python.sh'), shell=True)

        if not self.is_output_produced():
            raise FileNotFoundError('Problem in using mecoshark! No output was produced!')

    def is_output_produced(self):
        """
        Checks if output was produced for the process

        :return: boolean
        """

        output_path = os.path.join(self.output_path, self.projectname, 'python')

        if not os.path.exists(output_path):
            return False

        output_path = os.path.join(output_path, os.listdir(output_path)[0])
        number_of_files = len([name for name in os.listdir(output_path) if name.endswith('.csv')])

        if number_of_files == 11:
            return True

        return False

    def process(self, revision, url, options, debug_level):
        """
        See: :func:`~mecoshark.processor.baseprocessor.BaseProcessor.process`

        Processes the given revision.
        1) executes sourcemeter
        2) creates :class:`~mecoshark.resultparser.sourcemeterparser.SourcemeterParser` instance
        3) calls :func:`~mecoshark.resultparser.sourcemeterparser.SourcemeterParser.store_data`

        :param revision: revision
        :param url: url of the project that is analyzed
        :param options: options for execution
        :param debug_level: debugging_level
        """
        logger.setLevel(debug_level)
        self.execute_sourcemeter()
        meco_path = os.path.join(self.output_path, self.projectname, 'python')

        output_path = os.path.join(meco_path, os.listdir(meco_path)[0])

        parser = SourcemeterParser(output_path, self.input_path, url, revision, debug_level)
        parser.store_data()

        shutil.rmtree(os.path.join(self.output_path), True)




