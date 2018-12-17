import json
import logging
import logging.config
import os
import sys

from mecoshark.mecosharkapp import MecoSHARK
from pycoshark.utils import get_base_argparser


def setup_logging(default_path=os.path.dirname(os.path.realpath(__file__)) + "/mecoshark/loggerConfiguration.json",
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

    parser = get_base_argparser('Calculates metrics & performs clone detection for the given version.', '1.0.0')
    parser.add_argument('-i', '--input', help='Path to the repository.',
                        required=True, type=readable_dir)
    parser.add_argument('-o', '--output', help='Directory, which can be used as output.',
                        required=True, type=writable_dir)
    parser.add_argument('-pn', '--project_name', help='Name of the Project.')
    parser.add_argument('-r', '--revision', help='Hash of the revision.', required=True)
    parser.add_argument('-u', '--repository_url', help='URL of the project (e.g., GIT Url).', required=True)
    parser.add_argument('--debug', help='Specifies the debug level', choices=['INFO', 'DEBUG', 'WARNING', 'ERROR'],
                        default='DEBUG')
    parser.add_argument('--makefile-contents', help='Makefile contents', default=None)

    try:
        args = parser.parse_args()
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    logger.debug("Got the following parameters. Input: %s, Output: %s, Project name: %s, Revision: %s, URL: %s, Makefile-contents: %s" %
                 (args.input, args.output, args.project_name, args.revision, args.repository_url, args.makefile_contents))

    mecoshark = MecoSHARK(args.input, args.output, args.project_name, args.revision, args.repository_url, args.makefile_contents, args.db_database,
                          args.db_hostname, args.db_port, args.db_user, args.db_password, args.db_authentication,
                          args.debug, args.ssl)
    mecoshark.process_revision()


if __name__ == "__main__":
    start()