import logging
import subprocess
import shutil
import sys
import os
import timeit

from mongoengine import connect

from mecoshark.utils import find_correct_processor


class MecoSHARK(object):

    def __init__(self, input, output, revision, url, options, db_name, db_host, db_port, db_user, db_password,
                 db_authentication):
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
        languages = str(output).split('\\n')
        languages = {x:languages.count(x) for x in languages}
        languages.pop('', None)
        languages.pop('', None)
        languages.pop('\'', None)
        languages.pop('b\'', None)
        return languages
