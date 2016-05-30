from mecoshark.resultparser.sourcemeterparser import SourcemeterParser
import glob
import os
import csv
import copy
import sys
from mecoshark.resultparser.mongomodels import ClazzState, Clazz, Interface, InterfaceState, Enum, EnumState, Method, \
    MethodState, Namespace, NamespaceState, Function, FunctionState, Structure, StructureState, UnionState, Union


class SourcemeterCParser(SourcemeterParser):

    def __init__(self, output_path, input_path, url, revisionhash):
        super().__init__(output_path, input_path, url, revisionhash)
        self.stored_namespaces = {}
        self.stored_structures = {}
        self.stored_unions = {}

    def store_data(self):
        self.logger.info("Parsing & storing file metric data...")
        self.store_file_csv()
        self.logger.info("Finished parsing & storing file metric data!")

        self.logger.info("Parsing & storing component metric data...")
        self.store_components_csv()
        self.logger.info("Finished parsing & storing component metric data!")

        self.logger.info("Parsing & storing namespace metric data...")
        self.store_namespaces_csv()
        self.logger.info("Finished parsing & storing namespace metric data!")

        self.logger.info("Parsing & storing functions metric data...")
        self.store_functions_csv()
        self.logger.info("Finished parsing & storing functions metric data!")

        # We have the problem, that we have a lot of dependencies, thats why we need to put classes, methods, enums,
        # interfaces, and methods together and sort them correctly so that we can store them without any problems
        self.logger.info("Parsing & storing classes, interfaces, enums, methods, unions, and structures metric data...")
        self.prepare_csv_files()
        self.store_c_data()
        self.logger.info("Finished parsing & storing classes, interfaces, enums, methods, unions, and structures  "
                         "metric data!")

    def store_functions_csv(self):
        functions_csv_path = glob.glob(os.path.join(self.output_path, "*-Function.csv"))[0]
        with open(functions_csv_path) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                sanitized_path = self.sanitize_long_name(row['Path'])

                # if files were never committed to git, continue (e.g., files that are created during make)
                if sanitized_path not in self.stored_files:
                    continue

                function = Function.objects(projectId=self.projectid, fileId=self.stored_files[sanitized_path],
                                            longName=row['LongName']) \
                    .upsert_one(projectId=self.projectid, fileId=self.stored_files[sanitized_path], name=row["Name"],
                                longName=row['LongName'])
                self.stored_functions[row['ID']] = function.id

                metrics_dict = self.sanitize_metrics_dictionary(copy.deepcopy(row))

                FunctionState.objects(functionId=function.id, revisionHash=self.revisionHash)\
                    .upsert_one(functionId=function.id, revisionHash=self.revisionHash, metrics=metrics_dict,
                                startLine=row['Line'], endLine=row['EndLine'], startColumn=row['Column'],
                                endColumn=row['EndColumn'], componentIds=self.get_component_ids(row['Component']))

    def store_namespaces_csv(self):
        namespace_csv_path = glob.glob(os.path.join(self.output_path, "*-Namespace.csv"))[0]
        with open(namespace_csv_path) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                long_name = row['LongName']
                if not long_name:
                    long_name = row['Name']

                namespace = Namespace.objects(projectId=self.projectid, longName=long_name) \
                    .upsert_one(projectId=self.projectid, name=row["Name"], longName=long_name)
                self.stored_namespaces[row['ID']] = namespace.id

                metrics_dict = self.sanitize_metrics_dictionary(copy.deepcopy(row))

                if row['Parent'] and row['Parent'] in self.stored_namespaces:
                    NamespaceState.objects(namespaceId=namespace.id, revisionHash=self.revisionHash) \
                        .upsert_one(namespaceId=namespace.id, revisionHash=self.revisionHash, metrics=metrics_dict,
                                    componentIds=self.get_component_ids(row['Component']),
                                    parentNamespace=self.stored_namespaces[row['Parent']])
                else:
                    NamespaceState.objects(namespaceId=namespace.id, revisionHash=self.revisionHash) \
                        .upsert_one(namespaceId=namespace.id, revisionHash=self.revisionHash, metrics=metrics_dict,
                                    componentIds=self.get_component_ids(row['Component']))

    def get_parent_type(self, parent, artifact_type):
        mongo_names = {'class': {'stored_namespaces': 'namespaceId', 'stored_classes': 'parentClazzId',
                                 'stored_methods': 'methodId', 'stored_interfaces': 'interfaceId',
                                 'stored_enums': 'enumId', 'stored_structures': 'structureId',
                                 'stored_unions': 'unionId'},
                       'interface': {'stored_namespaces': 'namespaceId', 'stored_classes': 'clazzId',
                                     'stored_methods': 'methodId', 'stored_interfaces': 'parentInterfaceId',
                                     'stored_enums': 'enumId', 'stored_structures': 'structureId',
                                     'stored_unions': 'unionId'},
                       'enum': {'stored_namespaces': 'namespaceId', 'stored_classes': 'clazzId',
                                'stored_methods': 'methodId', 'stored_interfaces': 'interfaceId',
                                'stored_enums': 'parentEnumId', 'stored_structures': 'structureId',
                                'stored_unions': 'unionId'},
                       'method': {'stored_namespaces': 'namespaceId', 'stored_classes': 'clazzId',
                                  'stored_methods': 'parentMethodId', 'stored_interfaces': 'interfaceId',
                                  'stored_enums': 'enumId', 'stored_structures': 'structureId',
                                  'stored_unions': 'unionId'},
                       'structure':{'stored_namespaces': 'namespaceId', 'stored_classes': 'clazzId',
                                    'stored_methods': 'methodId', 'stored_interfaces': 'interfaceId',
                                    'stored_enums': 'enumId', 'stored_structures': 'parentStructureId',
                                    'stored_unions': 'unionId'},
                       'union': {'stored_namespaces': 'namespaceId', 'stored_classes': 'clazzId',
                                 'stored_methods': 'methodId', 'stored_interfaces': 'interfaceId',
                                 'stored_enums': 'enumId', 'stored_structures': 'structureId',
                                 'stored_unions': 'parentUnionId'}
                       }
        rdata = False
        name = False

        for d in ['stored_namespaces', 'stored_classes', 'stored_methods', 'stored_interfaces', 'stored_enums',
                  'stored_structures', 'stored_unions']:
            if parent in getattr(self, d):
                rdata = getattr(self, d)[parent]
                name = mongo_names[artifact_type][d]
                break

        if not rdata or not name:
            raise Exception('Error determining state')
        return name, rdata

    def store_c_data(self):
        classes_csv_path = glob.glob(os.path.join(self.output_path, "all_temp.csv"))[0]
        with open(classes_csv_path) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                long_name = self.sanitize_long_name(row['Path'])
                metrics_dict = self.sanitize_metrics_dictionary(copy.deepcopy(row))

                dat = {'revisionHash': self.revisionHash, 'startLine': row['Line'],
                       'endLine': row['EndLine'], 'startColumn': row['Column'], 'endColumn': row['EndColumn'],
                       'metrics': metrics_dict, 'componentIds': self.get_component_ids(row['Component'])}

                if row['type'] == 'class':
                    clazz = Clazz.objects(projectId=self.projectid, fileId=self.stored_files[long_name],
                                          longName=row['LongName'])\
                        .upsert_one(projectId=self.projectid, fileId=self.stored_files[long_name], name=row['Name'],
                                    longName=row['LongName'])
                    self.stored_classes[row['ID']] = clazz.id
                    dat['clazzId'] = clazz.id

                    try:
                        name, data = self.get_parent_type(row['Parent'], row['type'])
                        dat[name] = data
                        ClazzState.objects(clazzId=clazz.id, revisionHash=self.revisionHash)\
                            .upsert_one(**dat)
                    except Exception as e:
                        self.logger.error("Error in saving class %s. Error: %s" %(row['LongName'], str(e)))

                elif row['type'] == 'interface':
                    interface = Interface.objects(projectId=self.projectid, fileId=self.stored_files[long_name],
                                                  longName=row['LongName'])\
                        .upsert_one(projectId=self.projectid, fileId=self.stored_files[long_name], name=row['Name'],
                                    longName=row['LongName'])
                    self.stored_interfaces[row['ID']] = interface.id
                    dat['interfaceId'] = interface.id

                    try:
                        name, data = self.get_parent_type(row['Parent'], row['type'])
                        dat[name] = data
                        InterfaceState.objects(interfaceId=interface.id, revisionHash=self.revisionHash)\
                            .upsert_one(**dat)
                    except Exception as e:
                        self.logger.error("Error in saving interface %s. Error: %s" %(row['LongName'], str(e)))

                elif row['type'] == 'enum':
                    enum = Enum.objects(projectId=self.projectid, fileId=self.stored_files[long_name],
                                        longName=row['LongName'])\
                        .upsert_one(projectId=self.projectid, fileId=self.stored_files[long_name], name=row['Name'],
                                    longName=row['LongName'])
                    self.stored_enums[row['ID']] = enum.id
                    dat['enumId'] = enum.id

                    try:
                        name, data = self.get_parent_type(row['Parent'], row['type'])
                        dat[name] = data
                        EnumState.objects(enumId=enum.id, revisionHash=self.revisionHash)\
                            .upsert_one(**dat)
                    except Exception as e:
                        self.logger.error("Error in saving enum %s. Error: %s" %(row['LongName'], str(e)))

                elif row['type'] == 'method':
                    method = Method.objects(projectId=self.projectid, fileId=self.stored_files[long_name],
                                            longName=row['LongName'])\
                                .upsert_one(projectId=self.projectid, fileId=self.stored_files[long_name],
                                            name=row['Name'], longName=row['LongName'])
                    self.stored_methods[row['ID']] = method.id
                    dat['methodId'] = method.id

                    try:
                        name, data = self.get_parent_type(row['Parent'], row['type'])
                        dat[name] = data
                        MethodState.objects(methodId=method.id, revisionHash=self.revisionHash)\
                            .upsert_one(**dat)
                    except Exception as e:
                        self.logger.error("Error in saving method %s. Error: %s" %(row['LongName'], str(e)))

                elif row['type'] == 'structure':
                    structure = Structure.objects(projectId=self.projectid, fileId=self.stored_files[long_name],
                                            longName=row['LongName'])\
                                .upsert_one(projectId=self.projectid, fileId=self.stored_files[long_name],
                                            name=row['Name'], longName=row['LongName'])
                    self.stored_structures[row['ID']] = structure.id
                    dat['structureId'] = structure.id

                    try:
                        name, data = self.get_parent_type(row['Parent'], row['type'])
                        dat[name] = data
                        StructureState.objects(structureId=structure.id, revisionHash=self.revisionHash)\
                            .upsert_one(**dat)
                    except Exception as e:
                        self.logger.error("Error in saving structure %s. Error: %s" %(row['LongName'], str(e)))

                elif row['type'] == 'union':
                    union = Union.objects(projectId=self.projectid, fileId=self.stored_files[long_name],
                                            longName=row['LongName'])\
                                .upsert_one(projectId=self.projectid, fileId=self.stored_files[long_name],
                                            name=row['Name'], longName=row['LongName'])
                    self.stored_unions[row['ID']] = union.id
                    dat['unionId'] = union.id

                    try:
                        name, data = self.get_parent_type(row['Parent'], row['type'])
                        dat[name] = data
                        UnionState.objects(unionId=union.id, revisionHash=self.revisionHash)\
                            .upsert_one(**dat)
                    except Exception as e:
                        self.logger.error("Error in saving union %s. Error: %s" %(row['LongName'], str(e)))

    def prepare_csv_files(self):
        all_csv_paths = {'class': glob.glob(os.path.join(self.output_path, "*-Class.csv"))[0],
                         'enum': glob.glob(os.path.join(self.output_path, "*-Enum.csv"))[0],
                         'interface':  glob.glob(os.path.join(self.output_path, "*-Interface.csv"))[0],
                         'method': glob.glob(os.path.join(self.output_path, "*-Method.csv"))[0],
                         'structure': glob.glob(os.path.join(self.output_path, "*-Structure.csv"))[0],
                         'union': glob.glob(os.path.join(self.output_path, "*-Union.csv"))[0]
                         }

        all_csvs_together = []
        for name, path in all_csv_paths.items():
            with open(path) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row['type'] = name
                    row['sortKey'] = row['Parent'].strip('L')

                    if row['LongName'] and row['LongName'] != '__UNNAMED__':
                        all_csvs_together.append(row)

        sorted_csvs = sorted(all_csvs_together, key=lambda k: int(k['sortKey']))

        with open(os.path.join(self.output_path, "all_temp.csv"), 'w') as csvfile:
            fieldnames = ['ID', 'Name', 'LongName', 'Parent', 'Component', 'RealizationLevel', 'Path', 'Line', 'Column',
                          'EndLine', 'EndColumn', 'CC', 'CCL', 'CCO', 'CI', 'CLC', 'CLLC', 'LDC', 'LLDC', 'LCOM5', 'NL',
                          'NLE', 'WMC', 'CBO', 'CBOI', 'NII', 'NOI', 'RFC', 'AD', 'CD', 'CLOC', 'DLOC', 'PDA', 'PUA',
                          'TCD', 'TCLOC', 'DIT', 'NOA', 'NOC', 'NOD', 'NOP', 'LLOC', 'LOC', 'NA', 'NG', 'NLA', 'NLG',
                          'NLM', 'NLPA', 'NLPM', 'NLS', 'NM', 'NOS', 'NPA', 'NPM', 'NS', 'TLLOC', 'TLOC', 'TNA', 'TNG',
                          'TNLA', 'TNLG', 'TNLM', 'TNLPA', 'TNLPM', 'TNLS', 'TNM', 'TNOS', 'TNPA', 'TNPM', 'TNS',
                          'McCC', 'NUMPAR', 'WarningBlocker', 'WarningCritical', 'WarningInfo', 'WarningMajor',
                          'WarningMinor', 'type', 'sortKey']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            not_finished = True
            written_ids = []
            while not_finished:
                for row in sorted_csvs:
                    if (row['Parent'] in self.stored_namespaces or row['Parent'] in self.stored_functions) \
                            and row['ID'] not in written_ids:
                        written_ids.append(row['ID'])
                        writer.writerow(row)

                    if row['Parent'] in written_ids and row['ID'] not in written_ids:
                        written_ids.append(row['ID'])
                        writer.writerow(row)

                    if len(written_ids) == len(sorted_csvs):
                        not_finished = False
