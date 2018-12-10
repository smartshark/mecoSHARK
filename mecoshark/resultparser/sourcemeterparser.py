import copy
import csv
import glob
import logging
import os
import sys

from mongoengine import DoesNotExist

from pycoshark.mongomodels import Project, VCSSystem, VCSSubmodule, Commit, File, CodeGroupState, CodeEntityState, CloneInstance
from pycoshark.utils import get_code_entity_state_identifier, get_code_group_state_identifier

logger = logging.getLogger("sourcemeter_parser")


class SourcemeterParser(object):
    """
    Parser that parses the results from sourcemeter

    :property output_path: path to an output directory, where files can be stored
    :property input_path: path to the revisionn that is used as input
    :property url: url to the repository of the project that is analyzed
    :property vcs_system_id: id of the vcs_system with the given url
    :property stored_files: list of files that are stored at the input path
    :property ordered_file_states: dictionary that have all results in an ordered manner (a state that have another as parent must be after this parent state)
    :property stored_file_states: states that were stored in the mongodb
    :property stored_meta_package_states: meta package states that were stored in the mongodb
    :property input_files: list of input files
    :property commit_id: id of the commit for which the data should be stored. :class:`bson.objectid.ObjectId`
    """
    def __init__(self, output_path, input_path, project_name, url, revision_hash, debug_level):
        """
        Initialization

        :param output_path: path to an output directory, where files were stored
        :param input_path: path to the revision that is used as input
        :param url: url to the repository of the project that is analyzed
        :param revision_hash: hash of the revision, which is analyzed
        :param debug_level: debug level, like defined in :mod:`logging`

        """
        # Set variables
        self.output_path = output_path
        self.input_path = input_path
        self.project_name = project_name
        self.url = url
        self.revision_hash = revision_hash

        # Default dictionaries and lists
        self.ordered_file_states = {}
        self.stored_file_states = {}
        self.stored_meta_package_states = {}
        self.input_files = []

        # Get logger
        logger.setLevel(debug_level)

        # Get project id and find all stored files in the current input path (needed for java projects)
        self.vcs_system_id = self.get_vcs_system_id()
        self.commit_id = self.get_commit_id(self.vcs_system_id)

        self.stored_files = self.find_stored_files()

        # Prepare csv files
        self.prepare_csv_files()

    def get_commit_id(self, vcs_system_id):
        """
        Gets the commit id for the corresponding projectid and revision
        :param vcs_system_id: id of the vcs system. :class:`bson.objectid.ObjectId`

        :return: commit_id (:class:`bson.objectid.ObjectId`)
        """
        try:
            return Commit.objects(vcs_system_id=vcs_system_id, revision_hash=self.revision_hash).get().id
        except DoesNotExist:
            logger.error("Commit with vcs_system_id %s and revision %s does not exist" %
                              (vcs_system_id, self.revision_hash))
            sys.exit(1)

    def get_vcs_system_id(self):
        """
        Gets the project id for the given url
        :param url: url of the vcs_system

        :return: vcs_system_id (:class:`bson.objectid.ObjectId`)
        """
        try:
            project = Project.objects.get(name=self.project_name)
            return VCSSystem.objects(url=self.url, project_id=project.id).get().id
        except DoesNotExist:
            logger.error("VCSSystem with the url %s does not exist in the database! Execute vcsSHARK first!" % self.url)
            sys.exit(1)

    def find_stored_files(self):
        """
        We need to find all files that are stored in the input path. This is needed to link the files that were parsed
        with the files that are already stored via vcsSHARK.
        :return: dictionary with file path as key and id as value (from vcsshark results)
        """
        # get list of files in input_path
        self.input_files = []
        for root, dirs, files in os.walk(self.input_path, topdown=True):
            for name in files:
                full_file_path = path_join(root, name).replace(self.input_path, "")

                # Filter out git directory
                if not full_file_path.startswith("/.git/"):
                    self.input_files.append(full_file_path)

        # get all stored files of the project
        stored_files = {}
        for file in File.objects(vcs_system_id=self.vcs_system_id):
            stored_files[file.path] = file.id

        # get all stored files from submodules
        submodules = VCSSystem \
            .objects(id=self.vcs_system_id) \
            .get() \
            .submodules
        submodules = [VCSSubmodule.objects(id=id).get() for id in submodules]
        for submodule in submodules:
            for file in File.objects(vcs_system_id=submodule.vcs_system_id):
                stored_files[path_join(submodule.path, file.path)] = file.id

        return stored_files

    @staticmethod
    def get_csv_file(path):
        """
        Return a filepath or none if nothing is found.

        :param path: path to file (regex)

        :return: filepath or none
        """
        result = glob.glob(path)
        if len(result) > 0:
            return result[0]

        return None

    def prepare_csv_files(self):
        """
        Prepares the csv files generated by SourceMeter by creating a sort key and sort it after it
        """
        all_csv_paths = {
            'class': self.get_csv_file(os.path.join(self.output_path, "*-Class.csv")),
            'enum': self.get_csv_file(os.path.join(self.output_path, "*-Enum.csv")),
            'interface':  self.get_csv_file(os.path.join(self.output_path, "*-Interface.csv")),
            'method': self.get_csv_file(os.path.join(self.output_path, "*-Method.csv")),
            'annotation': self.get_csv_file(os.path.join(self.output_path, "*-Annotation.csv")),
            'attribute': self.get_csv_file(os.path.join(self.output_path, "*-Attribute.csv")),
            'component': self.get_csv_file(os.path.join(self.output_path, "*-Component.csv")),
            'file': self.get_csv_file(os.path.join(self.output_path, "*-File.csv")),
            'function': self.get_csv_file(os.path.join(self.output_path, "*-Function.csv")),
            'module': self.get_csv_file(os.path.join(self.output_path, "*-Module.csv")),
            'package': self.get_csv_file(os.path.join(self.output_path, "*-Package.csv")),
            'namespace': self.get_csv_file(os.path.join(self.output_path, "*-Namespace.csv")),
            'structure': self.get_csv_file(os.path.join(self.output_path, "*-Structure.csv")),
            'union': self.get_csv_file(os.path.join(self.output_path, "*-Union.csv")),
        }

        file_states = []
        for name, path in all_csv_paths.items():
            if path is not None:
                logger.info("Open path: "+path)
                with open(path) as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        row['type'] = name

                        if name == 'file':
                            row['sortKey'] = '2'
                            row['Path'] = row['LongName']
                            file_states.append(row)
                            continue

                        if 'Parent' in row:
                            if row['Parent'] == '__LogicalRoot__':
                                row['sortKey'] = '1'
                                file_states.append(row)
                            else:
                                row['sortKey'] = row['Parent'].strip('L')
                                file_states.append(row)
                        else:
                            row['sortKey'] = '0'
                            file_states.append(row)

        file_states = sorted(file_states, key=lambda k: int(k['sortKey']))
        self.ordered_file_states = self.sort_for_parent(file_states)

    @staticmethod
    def sort_for_parent(state_dict):
        """
        Sorts the given dictionary in a way, that the parent states of the states must be before it.
        Special rules apply for file states, as they do not have any parents.


        :param state_dict: dictionary of states that should be ordered
        :return: ordered dictionary

        .. NOTE:: Example: X has parent Y, Y has parent Z. Therefore, it would be ordered:\
        Z -> Y -> X
        """
        not_finished = True
        new_dict = []
        written_ids = []

        while not_finished:
            for row in state_dict:
                if 'Parent' not in row and row['ID'] not in written_ids:
                    written_ids.append(row['ID'])
                    new_dict.append(row)

                if 'Parent' in row and row['ID'] not in written_ids and (row['Parent'] in written_ids
                                                                         or row['Parent'] == '__LogicalRoot__'
                                                                         or row['type'] == 'file'):
                    written_ids.append(row['ID'])
                    new_dict.append(row)

                if len(state_dict) == len(written_ids):
                    not_finished = False

        return new_dict

    def store_data(self):
        """
        Call to store data: If they have 'Path' in the row, file states data is stored. Otherwise, meta package data

        :return:
        """
        for row in self.ordered_file_states:
            if 'Path' in row:
                self.store_file_states_data(row)
            else:
                self.store_meta_package_data(row)

        self.store_clone_data()
        self.store_extra_data()

    def store_extra_data(self):
        """
        Call to store extra data. For java this would be the PMD file, for C/C++ the cppcheck file, and for
        python the pylint file.
        :return:
        """

        # Check which file is found
        pmd_file_path = glob.glob(os.path.join(self.output_path, "*-PMD.txt"))
        #pylint_file_path = glob.glob(os.path.join(self.output_path, "*-Pylint.txt"))

        if pmd_file_path:
            self.parse_pmd_file(pmd_file_path[0])
        #elif pylint_file_path:
        #    self.parse_pylint_file(pylint_file_path[0])

    def parse_pmd_file(self, path):
        logger.info("Parsing & storing pmd warnings...")
        with open(path) as pmd_file:
            data = pmd_file.readlines()

        # Go through all warnings that pmd reported
        file_warnings = {}
        for line in data:
            line = line.strip()
            parts = line.split(":")
            file_parts = parts[0].strip()
            pmd_type = parts[1].strip()
            message = parts[2].strip()

            file_path = file_parts.split("(")[0]
            file_path = file_path.replace(self.input_path.rstrip("/") + "/", "")
            line_number = file_parts.split("(")[1].strip(")")

            warnings = file_warnings.get(file_path, list())
            warnings.append({"ln": int(line_number), "l_ty": pmd_type, "msg": message})
            file_warnings[file_path] = warnings

        logger.debug("Found the following pmd warnings: %s" % file_warnings)

        for file_path, data in file_warnings.items():

            try:
                # Get file id
                m_file = File.objects(path=file_path, vcs_system_id=self.vcs_system_id).get()

                # Get code entity state
                identifier = get_code_entity_state_identifier(file_path, self.commit_id, m_file.id)
                m_ces = CodeEntityState.objects(s_key=identifier).get()
                m_ces.linter.clear()

                for warnings in data:
                    m_ces.linter.append(warnings)

                # Save code entity state
                m_ces.save()
            except DoesNotExist:
                logger.warning("Code Entity State for file %s does not exist!" % file_path)

    def get_component_ids(self, row_component_ids):
        """
        Function that gets the component ids from the component ids string.

        :param row_component_ids: component ids string
        :return: ObjectIds of all components as list (:class:`bson.objectid.ObjectId`)
        """
        # get list of objectids for all components in the csv file
        row_component_ids = row_component_ids.split(",")
        component_object_ids = []
        for row_component_id in row_component_ids:
            component_object_ids.append(self.stored_meta_package_states[row_component_id.strip()])
        return component_object_ids

    def store_meta_package_data(self, row):
        """
        Stores the meta package data.
        Fills the stored_meta_package_states property for less database communication.

        :param row: row that is processed

        .. NOTE:: Meta packages do not have a direct connection to files from a revision. It consists of a set of states.
        """
        long_name = self.sanitize_long_name(row['LongName'])
        metrics_dict = self.sanitize_metrics_dictionary(copy.deepcopy(row))

        cg_parent_ids = []
        if 'Parent' in row and row['Parent'] in self.stored_meta_package_states:
            cg_parent_ids.append(self.stored_meta_package_states[row['Parent']])

        if 'Component' in row:
            cg_parent_ids.extend(self.get_component_ids(row['Component']))

        s_key = get_code_group_state_identifier(long_name, self.commit_id)
        tmp = {'set__metrics__{}'.format(k): v for k, v in metrics_dict.items()}
        tmp['s_key'] = s_key
        tmp['long_name'] = long_name
        tmp['commit_id'] = self.commit_id
        tmp['cg_type'] = row['type']
        tmp['cg_parent_ids'] = cg_parent_ids

        state_id = CodeGroupState.objects(s_key=s_key).upsert_one(**tmp).id

        self.stored_meta_package_states[row['ID']] = state_id

    def store_file_states_data(self, row):
        """
        Stores the file states data.
        Fills the stored_file_states property for less database communication.

        :param row: row that is processed:

        .. NOTE:: File states have a direct connection to a file from a revision.
        """
        path_name = self.sanitize_long_name(row['Path'])

        # We only need to sanitize the long name for files, Otherwise we store it like it comes out of sourcemeter
        if row['type'] == 'file':
            long_name = self.sanitize_long_name(row['LongName'])
        else:
            long_name = row['LongName']

        cg_ids = []
        ce_parent_id = None
        if 'Parent' in row and row['Parent'] in self.stored_meta_package_states:
            cg_ids.append(self.stored_meta_package_states[row['Parent']])
        elif 'Parent' in row and row['Parent'] in self.stored_file_states:
            ce_parent_id = self.stored_file_states[row['Parent']]
        elif 'Parent' in row and row['type'] != 'file':
            logger.warning("ERROR! Parent not found for %s!" % row)

        if 'Component' in row:
            cg_ids.extend(self.get_component_ids(row['Component']))

        start_line = None
        end_line = None
        start_column = None
        end_column = None
        if 'Line' in row and 'EndLine' in row and 'Column' in row and 'EndColumn' in row:
            start_line = row['Line']
            end_line = row['EndLine']
            start_column = row['Column']
            end_column = row['EndColumn']

        try:
            s_key = get_code_entity_state_identifier(long_name, self.commit_id, self.stored_files[path_name])
            tmp = {'set__metrics__{}'.format(k): v for k, v in self.sanitize_metrics_dictionary(copy.deepcopy(row)).items()}
            tmp['s_key'] = s_key
            tmp['long_name'] = long_name
            tmp['commit_id'] = self.commit_id
            tmp['file_id'] = self.stored_files[path_name]
            tmp['ce_type'] = row['type']
            tmp['cg_ids'] = cg_ids
            tmp['ce_parent_id'] = ce_parent_id
            tmp['start_line'] = start_line
            tmp['end_line'] = end_line
            tmp['start_column'] = start_column
            tmp['end_column'] = end_column

            state_id = CodeEntityState.objects(s_key=s_key).upsert_one(**tmp).id
            self.stored_file_states[row['ID']] = state_id
        except KeyError:
            # This should not happen, but it can happen, e.g., for the conftest.cpp file for C/c++ projects, which
            # is just temporally created
            logger.warning("Could not store results for file %s" % path_name)

    def store_clone_data(self):
        """
        Parses and stores the cloning data that was generated by sourcemeter.
        """
        logger.info("Parsing & storing clone data...")
        clone_class_csv_path = glob.glob(os.path.join(self.output_path, "*-CloneClass.csv"))[0]
        clone_instance_csv_path = glob.glob(os.path.join(self.output_path, "*-CloneInstance.csv"))[0]

        clone_classes = {}
        with open(clone_class_csv_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                clone_classes[row['ID']] = self.sanitize_metrics_dictionary(copy.deepcopy(row))

        with open(clone_instance_csv_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                metrics_dict = self.sanitize_metrics_dictionary(copy.deepcopy(row))
                long_name = self.sanitize_long_name(row['Path'])

                tmp = {
                    'commit_id': self.commit_id,
                    'name': row['ID'],
                    'file_id': self.stored_files[long_name],
                    'clone_class': row['Parent'],
                    'clone_class_metrics': clone_classes[row['Parent']],
                    'clone_instance_metrics': metrics_dict,
                    'start_line': row['Line'],
                    'end_line': row['EndLine'],
                    'start_column': row['Column'],
                    'end_column': row['EndColumn']
                }

                CloneInstance.objects(name=row['ID'], commit_id=self.commit_id,
                                      file_id=self.stored_files[long_name]).upsert_one(**tmp)

        logger.info("Finished parsing & storing clone data!")

    @staticmethod
    def sanitize_metrics_dictionary(metrics):
        """
        Helper function, which sanitizes the csv reader row so that it only contains the metrics of it.

        :param metrics: csv reader row
        :return: dictionary of metrics
        """
        del metrics['Name']
        del metrics['ID']

        if 'LongName' in metrics:
            del metrics['LongName']

        if 'type' in metrics:
            del metrics['type']

        if 'sortKey' in metrics:
            del metrics['sortKey']

        if 'Component' in metrics:
            del metrics['Component']

        if 'Path' in metrics:
            del metrics['Path']

        if 'Parent' in metrics:
            del metrics['Parent']

        if 'WarningBlocker' in metrics:
            del metrics['WarningBlocker']

        if 'WarningCritical' in metrics:
            del metrics['WarningCritical']

        if 'WarningInfo' in metrics:
            del metrics['WarningInfo']

        if 'WarningMajor' in metrics:
            del metrics['WarningMajor']

        if 'WarningMinor' in metrics:
            del metrics['WarningMinor']

        if 'Line' in metrics:
            del metrics['Line']

        if 'EndLine' in metrics:
            del metrics['EndLine']

        if 'Column' in metrics:
            del metrics['Column']

        if 'EndColumn' in metrics:
            del metrics['EndColumn']

        for name, value in metrics.items():
            if not value:
                metrics[name] = float(0)
            else:
                try:
                    metrics[name] = float(value)
                except ValueError:
                    metrics[name] = value

        return metrics

    def sanitize_long_name(self, orig_long_name):
        """
        Sanitizes the long_name of the row.
        1) If the long_name has the input path in it: just strip it
        2) If the long_name has the output path in it: just strip it
        3) Otherwise: The long_name will be separated by "/" and joined together after the first part was split.

        :param orig_long_name: long_name of the row
        :return: sanitized long_name


        .. NOTE:: This is necessary, as the output of sourcemeter can be different based on which processor is used.
        """
        if self.input_path in orig_long_name:
            long_name = orig_long_name.replace(self.input_path + "/", "")
        elif self.output_path in orig_long_name:
            long_name = orig_long_name.replace(self.output_path + "/", "")
        else:
            long_name = "/".join(orig_long_name.strip("/").split('/')[1:])

            # if long_name is not an empty string
            if long_name:
                long_name = self.get_fullpath(long_name)
            else:
                long_name = orig_long_name

        if long_name is not None and long_name.startswith("/"):
            long_name = long_name.strip("/")

        return long_name

    def get_fullpath(self, long_name):
        """
        If the long_name is in the input files of the input path, it will return the corresponding file name

        :param long_name: long_name of the row
        :return: new long_name
        """
        for file_name in self.input_files:
            if file_name.endswith(long_name):
                return file_name
        return long_name
