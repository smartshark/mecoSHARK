import sys
import os

from mecoshark.processor.baseprocessor import BaseProcessor

def path_sanitize(path):
    return path.replace('\\', '/')
def expand_home(path):
    home_folder = os.path.expanduser('~') + "/"
    path = path.replace("~", home_folder) if path.startswith("~") else path
    return path_sanitize(path)

def find_plugins(pluginDir):
    """Finds all python files in the specified path and imports them. This is needed, if we want to
    detect automatically, which processor

    :param pluginDir: path to the plugin directory"""
    plugin_files = [x[:-3] for x in os.listdir(pluginDir) if x.endswith(".py")]
    sys.path.insert(0, pluginDir)
    for plugin in plugin_files:
        __import__(plugin)


def find_correct_processor(languages, output_path, input_path):
    """ Finds the correct processor by looking at the processor.supported_languages property

    :param language_identifier: string that represents the language (e.g., **java**)
    """
    # import processor plugins
    find_plugins(os.path.dirname(os.path.realpath(__file__))+"/processor")
    correct_processors = []
    for sc in BaseProcessor.__subclasses__():
        processor = sc(output_path, input_path)

        language_list = list(languages.keys())
        for language in language_list:
            if language in processor.supported_languages and languages[language] >= processor.threshold \
                    and processor.enabled:
                correct_processors.append(processor)

    return correct_processors
