import logging
import os
import unittest

from mecoshark.mecosharkapp import MecoSHARK


class MecoSHARKTest(unittest.TestCase):

    def setUp(self):
        self.input_path_python = os.path.dirname(os.path.realpath(__file__)) + '/data/python_project'
        self.input_path_java = os.path.dirname(os.path.realpath(__file__)) + '/data/java_project'
        self.out = os.path.dirname(os.path.realpath(__file__)) + '/data/out'

    def test_language_detection_java(self):
        mecosharkapp = MecoSHARK(self.input_path_java, self.out, None, None, None, None, None, None, None,
                                 None, None, logging.DEBUG)
        languages = mecosharkapp.detect_languages()

        # 6 ansic files, 22 java files, 28 files overall
        expected_languages = {
            'ansic': 6.0/28.0,
            'java': 22.0/28.0
        }
        self.assertEqual(expected_languages, languages)

    def test_language_detection_python(self):
        mecosharkapp = MecoSHARK(self.input_path_python, self.out, None, None, None, None, None, None, None,
                                 None, None, logging.DEBUG)
        languages = mecosharkapp.detect_languages()

        # 21 python files, 21 files overall
        expected_languages = {
            'python': 21.0/21.0
        }
        self.assertEqual(expected_languages, languages)