import logging
import subprocess
import shutil
import sys
import os
import timeit

from mongoengine import connect

from mecoshark.utils import find_correct_processor
from pycoshark.utils import create_mongodb_uri_string

logger = logging.getLogger('mecoshark_main')


class MecoSHARK(object):
    """
    Main app for the mecoshark plugin
    """

    def __init__(self, input, output, project_name, revision, url, makefile_contents, db_name, db_host, db_port, db_user, db_password,
                 db_authentication, debug_level, ssl_enabled):
        """
        Main runner of the mecoshark app

        :param input: path to the revision that is used as input
        :param output: path to an output directory, where files can be stored
        :param revision: string of the revision hash
        :param url: url of the project that is analyzed
        :param makefile_contents: contents of the makefile (e.g., for the c processor)
        :param db_name: name of the database
        :param db_host: name of the host where the mongodb is running
        :param db_port: port on which the mongodb listens on
        :param db_user: username of the mongodb user
        :param db_password: password for the mongodb user
        :param db_authentication: name of the database that is used as authentication
        :param debug_level: debug level like defined in :mod:`logging`

        .. WARNING:: URL must be the same as the url that was stored in the mongodb by vcsSHARK!
        """
        home_folder = os.path.expanduser('~')+"/"
        logger.setLevel(debug_level)
        self.project_name = project_name
        self.debug_level = debug_level
        self.input_path = input.replace("~", home_folder)
        self.output_path = output.replace("~", home_folder)
        self.makefile_contents = makefile_contents
        self.revision = revision
        self.url = url

        uri = create_mongodb_uri_string(db_user, db_password, db_host, db_port, db_authentication, ssl_enabled)
        # connect to mongodb
        connect(db_name, host=uri)

    def process_revision(self):
        """
        Processes a revision. First the language is detected, that the system uses, after that
        the correct processors are found, which can be used for this language and the process method is called.
        """
        languages = self.detect_languages()

        # Measure execution time
        start_time = timeit.default_timer()

        processors = find_correct_processor(languages, self.output_path, self.input_path)
        non_working_processors = 0
        for processor in processors:
            logger.info("Executing: %s" % processor.__class__.__name__)
            try:
                processor.process(self.project_name, self.revision, self.url, self.makefile_contents, self.debug_level)
            except FileNotFoundError as e:
                logger.error(e)
                non_working_processors += 1

            # SmartSHARK needs an error in its std.err, but we say the whole execution failed only if all processors
            # that were executed are failing
            if len(processors) == non_working_processors:
                sys.stderr.write("fatal error. All processors failed!\n")
                sys.exit(1)

        elapsed = timeit.default_timer() - start_time
        logger.info("Execution time: %0.5f s" % elapsed)

    def detect_languages(self):
        """
        Detects programming languages used in the input path
        """
        external_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'external')
        sloccount_path = os.path.join(external_path, 'sloccount2.26', 'sloccount')

        sloccount_temp = os.path.join(self.input_path, '.sloccount')
        os.makedirs(sloccount_temp, mode=0o777, exist_ok=True)

        command = "%s --datadir %s --details %s | awk -F '\t' '{print $2}'" % (sloccount_path, sloccount_temp,
                                                                               self.input_path)
        logger.info('Calling command: %s' % command)

        # suppress output to stderr, because we just need the langauges
        output = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL)

        try:
            languages = self.sanitize_sloccount_output(output)
        except Exception:
            logger.error('Problem in parsing sloccount output')
            sys.exit(1)

        logger.debug('Found the following languages: %s' % languages)

        all_files = sum(languages.values())
        for language in languages:
            language_part = int(languages[language]) / all_files
            languages[language] = language_part
            logger.debug('Language %s part: %f' % (language, language_part))

        logger.info("Found the following languages: "+','.join(languages))
        shutil.rmtree(sloccount_temp)

        return languages

    @staticmethod
    def sanitize_sloccount_output(output):
        """
        Method that sanitizes the sloccount output (because we read it directly from the command line)

        :param output: ouput that must be sanitized
        """
        languages = str(output).split('\\n')
        languages = {x:languages.count(x) for x in languages}
        languages.pop('', None)
        languages.pop('', None)
        languages.pop('\'', None)
        languages.pop('b\'', None)
        return languages
