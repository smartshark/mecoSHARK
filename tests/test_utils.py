import logging
import os
import unittest

from mecoshark.mecosharkapp import find_correct_processor
from mecoshark.processor.javaprocessor import JavaProcessor
from mecoshark.processor.pythonprocessor import PythonProcessor

class MecoSHARKTest(unittest.TestCase):

    def setUp(self):
        # Setup logging
        #logging.basicConfig(level=logging.DEBUG)
        self.input_path_python = os.path.dirname(os.path.realpath(__file__)) + '/data/python_project'
        self.input_path_java = os.path.dirname(os.path.realpath(__file__)) + '/data/java_project'
        self.out = os.path.dirname(os.path.realpath(__file__)) + '/data/out'

    def test_correct_processor_java(self):
        # 6 ansic files, 22 java files, 28 files overall
        languages = {
            'ansic': 6.0 / 28.0,
            'java': 22.0 / 28.0
        }
        processors = find_correct_processor(languages, self.out, self.input_path_java)
        java_processor = processors[0]
        self.assertEqual('JavaProcessor', type(java_processor).__name__)

    # python processor deactivated!
    def __test_correct_processor_python(self):
        # 21 python files, 21 files overall
        languages = {
            'python': 21.0 / 21.0
        }
        processors = find_correct_processor(languages, self.out, self.input_path_python)
        python_processor = processors[0]
        self.assertEqual('PythonProcessor', type(python_processor).__name__)
