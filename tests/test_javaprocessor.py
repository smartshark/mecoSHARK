import os
import shutil
import unittest
from pathlib import Path

import mock

from mecoshark.processor.javaprocessor import JavaProcessor


class JavaProcessorTest(unittest.TestCase):

    def setUp(self):
        self.input_path_java = os.path.dirname(os.path.realpath(__file__)) + '/data/java_project'
        self.out = os.path.dirname(os.path.realpath(__file__)) + '/data/out_java'
        self.projectname = os.path.basename(os.path.normpath(self.input_path_java))
        # Create fake output
        shutil.rmtree(self.out, ignore_errors=True)
        os.makedirs(self.out+'/'+self.projectname+'/java/timestamp')

    def test_output_produced_succeed(self):
        java_processor = JavaProcessor(self.out, self.input_path_java)

        # Create 12 fake files
        for i in range(0, 12):
            Path(self.out + '/' + self.projectname + '/java/timestamp/test' + str(i) + '.csv').touch()

        self.assertTrue(java_processor.is_output_produced())

    def test_output_produced_fails(self):
        java_processor = JavaProcessor(self.out, self.input_path_java)
        self.assertFalse(java_processor.is_output_produced())

    def test_output_produced_fails_too_less_csvs(self):
        java_processor = JavaProcessor(self.out, self.input_path_java)

        # Create 11 fake files
        for i in range(0, 11):
            Path(self.out + '/' + self.projectname + '/java/timestamp/test' + str(i) + '.csv').touch()

        self.assertFalse(java_processor.is_output_produced())

    def test_output_produced_fails_too_much_csvs(self):
        java_processor = JavaProcessor(self.out, self.input_path_java)

        # Create 13 fake files
        for i in range(0, 13):
            Path(self.out + '/' + self.projectname + '/java/timestamp/test' + str(i) + '.csv').touch()

        self.assertFalse(java_processor.is_output_produced())

    @mock.patch('subprocess.run')
    def test_language_detection_java(self, mock_subprocess):
        java_processor = JavaProcessor(self.out, self.input_path_java)

        # It should make a sys.exit call, as no ouput was produced
        with self.assertRaises(FileNotFoundError) as cm:
            java_processor.execute_sourcemeter()

        path_to_processors = os.path.dirname(os.path.realpath(__file__))+'/../mecoshark/processor/'
        new_path = os.path.abspath(path_to_processors)+'/../../external/sourcemeter/Java/SourceMeterJava'

        self.maxDiff = None
        expected_string = '#!/bin/sh\n' \
                          '%s -maximumThreads=4 ' \
                          '-projectName=java_project ' \
                          '-projectBaseDir=%s ' \
                          '-resultsDir=%s ' \
                          '-runAndroidHunter=false ' \
                          '-runMetricHunter=false ' \
                          '-runVulnerabilityHunter=false ' \
                          '-runFaultHunter=false ' \
                          '-runDCF=true ' \
                          '-runFB=false ' \
                          '-runPMD=true' % (new_path, self.input_path_java, self.out)

        # read out created analyze-dir
        with open(self.out+'/analyze-dir.sh', 'r') as file:
            output = file.read()

        self.assertEqual(expected_string, output)



