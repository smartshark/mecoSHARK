import os
import logging
import logging.config
import json
import sys
import argparse
from mecoshark.mecosharkapp import MecoSHARK


def setup_logging(default_path=os.path.dirname(os.path.realpath(__file__))+"/mecoshark/loggerConfiguration.json",
                  default_level=logging.INFO):
        """
        Setup logging configuration

        :param default_path: path to the logger configuration
        :param default_level: defines the default logging level if configuration file is not found
        (default:logging.INFO)
        """
        path = default_path
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = json.load(f)
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)


def writable_dir(prospective_dir):
    """ Function that checks if a path is a directory, if it exists and if it is writable and only
    returns true if all these three are the case

    :param prospective_dir: path to the directory"""

    prospective_dir = os.path.join(prospective_dir, 'mecoshark')
    if prospective_dir is not None:
        if not os.path.isdir(prospective_dir):
            os.makedirs(prospective_dir, exist_ok=True)
        if os.access(prospective_dir, os.W_OK):
            return prospective_dir
        else:
            raise Exception("output:{0} is not a writable dir".format(prospective_dir))


def readable_dir(prospective_dir):
    """ Function that checks if a path is a directory, if it exists and if it is accessible and only
    returns true if all these three are the case

    :param prospective_dir: path to the directory"""
    if prospective_dir != None:
        if not os.path.isdir(prospective_dir):
            raise Exception("input:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            return prospective_dir
        else:
            raise Exception("input:{0} is not a readable dir".format(prospective_dir))


def start():
    """
    Starts the application. First parses the different command line arguments and then it gives these to the mecoApp
    :return:
    """
    setup_logging()
    logger = logging.getLogger("mecoshark_main")
    logger.info("Starting mecoSHARK...")
    parser = argparse.ArgumentParser(description='Calculates metrics & performs clone detection for the given version.')
    parser.add_argument('-v', '--version', help='Shows the version', action='version', version='0.0.1')
    parser.add_argument('-i', '--input', help='Path to the repository.',
                        required=True, type=readable_dir)
    parser.add_argument('-o', '--output', help='Directory, which can be used as output.',
                        required=True, type=writable_dir)
    parser.add_argument('-r', '--rev', help='Hash of the revision.', required=True)
    parser.add_argument('-u', '--url', help='URL of the project (e.g., GIT Url).', required=True)
    parser.add_argument('-U', '--db-user', help='Database user name', default='root')
    parser.add_argument('-P', '--db-password', help='Database user password', default='root')
    parser.add_argument('-DB', '--db-database', help='Database name', default='smartshark')
    parser.add_argument('-H', '--db-hostname', help='Name of the host, where the database server is running', default='localhost')
    parser.add_argument('-p', '--db-port', help='Port, where the database server is listening', default=27017, type=int)
    parser.add_argument('-a', '--db-authentication', help='Name of the authentication database')
    parser.add_argument('--options', help='Optionstring in the form "option1=value1,option2=value2".')

    try:
        args = parser.parse_args()
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    parsed_options = {}
    if args.options:
        options = args.options.split(',')
        for option in options:
            option_parts = option.split('=')
            option_value = '='.join(option_parts[1:])
            option_value = option_value.replace("\\n", "\n")
            parsed_options[option_parts[0]] = option_value

    logger.debug("Got the following parameters. Input: %s, Output: %s, Revision: %s, URL: %s, Options: %s" %
                 (args.input, args.output, args.rev, args.url, parsed_options))

    mecoshark = MecoSHARK(args.input, args.output, args.rev, args.url, parsed_options, args.db_database,
                          args.db_hostname, args.db_port, args.db_user, args.db_password, args.db_authentication)
    mecoshark.process_revision()

if __name__ == "__main__":
    start()