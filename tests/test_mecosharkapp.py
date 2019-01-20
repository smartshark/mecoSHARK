import configparser
import logging
import os
import unittest

from mecoshark.mecosharkapp import MecoSHARK


class MecoSHARKTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create testconfig
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.realpath(__file__)) + "/data/used_test_config.cfg")

        cls.database = config['Database']['db_database']
        cls.host = config['Database']['db_hostname']
        cls.username = config['Database']['db_user']
        cls.password = config['Database']['db_password']
        cls.port = int(config['Database']['db_port'])
        cls.authentication_db = config['Database']['db_authentication']

    def setUp(self):
        self.input_path_python = os.path.dirname(os.path.realpath(__file__)) + '/data/python_project'
        self.input_path_java = os.path.dirname(os.path.realpath(__file__)) + '/data/java_project'
        self.out = os.path.dirname(os.path.realpath(__file__)) + '/data/out'

    def test_language_detection_java(self):
        mecosharkapp = MecoSHARK(self.input_path_java, self.out, "test", None, None, None, None, self.database, self.host, self.port,
                                 self.username, self.password, self.authentication_db, logging.DEBUG, False)
        languages = mecosharkapp.detect_languages()

        # 6 ansic files, 22 java files, 28 files overall
        expected_languages = {
            'ansic': 6.0/28.0,
            'java': 22.0/28.0
        }
        self.assertEqual(expected_languages, languages)

    def test_language_detection_python(self):
        mecosharkapp = MecoSHARK(self.input_path_python, self.out, "test", None, None, None, None, self.database, self.host, self.port,
                                 self.username, self.password, self.authentication_db, logging.DEBUG, False)
        languages = mecosharkapp.detect_languages()

        # 21 python files, 21 files overall
        expected_languages = {
            'python': 21.0/21.0
        }
        self.assertEqual(expected_languages, languages)