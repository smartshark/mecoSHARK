import logging
import subprocess
import shutil
import sys
import os
import timeit

from mongoengine import connect

from mecoshark.utils import find_correct_processor


class MecoSHARK(object):
    """ Main app for the mecoshark plugin


    :param input: path to the revision that is used as input
    :param output: path to an output directory, where files can be stored
    :param revision: string of the revision hash
    :param url: url of the project that is analyzed
    :param options: potential options (e.g., for the c processor)
    :param db_name: name of the database
    :param db_host: name of the host where the mongodb is running
    :param db_port: port on which the mongodb listens on
    :param db_user: username of the mongodb user
    :param db_password: password for the mongodb user
    :param db_authentication: name of the database that is used as authentication


    :property logger: logger, which is acquired via logging.getLogger("mecoshark_main")
    :property input_path: path to the revisionn that is used as input
    :property output_path: path to an output directory, where files can be stored
    :property options: potential options (e.g., for the c processor)
    :property revision: string of the revision hash
    :property url: url of the project that is analyzed
    :property projectname: name of the project (last part of input path)
    """


    def __init__(self, input, output, revision, url, options, db_name, db_host, db_port, db_user, db_password,
                 db_authentication):
        """
        Main runner of the mecoshark app
        """
        home_folder = os.path.expanduser('~')+"/"
        self.logger = logging.getLogger("mecoshark_main")
        self.input_path = input.replace("~", home_folder)
        self.output_path = output.replace("~", home_folder)
        self.options = options
        self.revision = revision
        self.url = url
        self.projectname = os.path.basename(os.path.normpath(input))

        # connect to mongodb
        connect(db_name, host=db_host, port=db_port, authentication_source=db_authentication, username=db_user,
                password=db_password, connect=False)

    def process_revision(self):
        """
        Processes a revision. First the language is detected, that the system uses, after that
        the correct processors are found, which can be used for this language and the process method is called.
        """
        languages = self.detect_languages()

        # Measure execution time
        start_time = timeit.default_timer()

        processors = find_correct_processor(languages, self.output_path, self.input_path)

        for processor in processors:
            self.logger.info("Executing: %s" % processor.__class__.__name__)
            processor.process(self.revision, self.url, self.options)

        elapsed = timeit.default_timer() - start_time
        self.logger.info("Execution time: %0.5f s" % elapsed)

    def detect_languages(self):
        """
        Detects programming languages used in the input path

        :return: languages that are used
        """
        external_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'external')
        sloccount_path = os.path.join(external_path, 'sloccount2.26', 'sloccount')

        command = sloccount_path+" --details "+self.input_path+" | awk -F '\t' '{print $2}'"
        self.logger.info('Calling command: %s' % command)
        output = subprocess.check_output(command, shell=True)

        languages = self.sanitize_sloccount_output(output)
        self.logger.debug('Found the following languages: %s' % languages)

        all_files = sum(languages.values())
        for language in languages:
            language_part = int(languages[language]) / all_files
            languages[language] = language_part
            self.logger.debug('Language %s part: %f' % (language, language_part))

        self.logger.info("Found the following languages: "+','.join(languages))

        return languages

    @staticmethod
    def sanitize_sloccount_output(output):
        """
        Method that sanitizes the sloccount output (because we read it directly from the command line)


        :param output: ouput that must be sanitized

        :return: sanitized output
        """
        languages = str(output).split('\\n')
        languages = {x:languages.count(x) for x in languages}
        languages.pop('', None)
        languages.pop('', None)
        languages.pop('\'', None)
        languages.pop('b\'', None)
        return languages
