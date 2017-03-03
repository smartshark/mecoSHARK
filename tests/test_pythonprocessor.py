import filecmp
import os
import unittest

import mock
import shutil

from pathlib import Path
from mecoshark.processor.pythonprocessor import PythonProcessor


class PythonProcessorTest(unittest.TestCase):

    def setUp(self):
        self.input_path_python = os.path.dirname(os.path.realpath(__file__)) + '/data/python_project'
        self.out = os.path.dirname(os.path.realpath(__file__)) + '/data/out_python'
        self.projectname = os.path.basename(os.path.normpath(self.input_path_python))

        # Create fake output
        shutil.rmtree(self.out, ignore_errors=True)
        os.makedirs(self.out + '/' + self.projectname + '/python/timestamp')

    def test_output_produced_fails(self):
        python_processor = PythonProcessor(self.out, self.input_path_python)
        self.assertFalse(python_processor.is_output_produced())

    def test_output_produced_succeed(self):
        python_processor = PythonProcessor(self.out, self.input_path_python)

        # Create 11 fake files
        for i in range(0, 11):
            Path(self.out + '/' + self.projectname + '/python/timestamp/test' + str(i) + '.csv').touch()

        self.assertTrue(python_processor.is_output_produced())

    def test_output_produced_fails_too_less_csvs(self):
        python_processor = PythonProcessor(self.out, self.input_path_python)

        # Create 11 fake files
        for i in range(0, 10):
            Path(self.out + '/' + self.projectname + '/python/timestamp/test' + str(i) + '.csv').touch()

        self.assertFalse(python_processor.is_output_produced())

    def test_output_produced_fails_too_much_csvs(self):
        python_processor = PythonProcessor(self.out, self.input_path_python)

        # Create 11 fake files
        for i in range(0, 12):
            Path(self.out + '/' + self.projectname + '/python/timestamp/test' + str(i) + '.csv').touch()

        self.assertFalse(python_processor.is_output_produced())

    @mock.patch('subprocess.run')
    def test_language_detection_python(self, mock_subprocess):
        python_processor = PythonProcessor(self.out, self.input_path_python)

        # It should make a sys.exit call, as no ouput was produced
        with self.assertRaises(SystemExit) as cm:
            python_processor.execute_sourcemeter()

        self.assertEqual(cm.exception.code, 1)

        path_to_processors = os.path.dirname(os.path.realpath(__file__))+'/../mecoshark/processor/'
        new_path = os.path.abspath(path_to_processors)+'/../../external/sourcemeter/Python/SourceMeterPython'

        expected_string = '#!/bin/sh\n' \
                          'cd %s\n' \
                          '%s -projectBaseDir:%s ' \
                          '-projectName:python_project ' \
                          '-resultsDir:%s ' \
                          '-runMetricHunter=false ' \
                          '-runFaultHunter=false ' \
                          '-runPylint=false ' \
                          '-runDCF=true\n' % (self.out, new_path, self.input_path_python, self.out)

        # Read out created analyzes script for sourcemeter
        with open(self.out+'/analyze_python.sh', 'r') as file:
            output = file.read()

        self.assertEqual(expected_string, output)




