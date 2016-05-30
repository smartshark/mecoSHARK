from mecoshark.resultparser.sourcemeterparser import SourcemeterParser
import glob
import os
import csv
import copy
from mecoshark.resultparser.mongomodels import ClazzState, Clazz, Interface, InterfaceState, Enum, EnumState, Method, \
    MethodState


class SourcemeterJavaParser(SourcemeterParser):

    def __init__(self, output_path, input_path, url, revisionhash):
        super().__init__(output_path, input_path, url, revisionhash)

    def store_data(self):
        self.logger.info("Parsing & storing file metric data...")
        self.store_file_csv()
        self.logger.info("Finished parsing & storing file metric data!")

        self.logger.info("Parsing & storing component metric data...")
        self.store_components_csv()
        self.logger.info("Finished parsing & storing component metric data!")

        self.logger.info("Parsing & storing package metric data...")
        self.store_packages_csv()
        self.logger.info("Finished parsing & storing package metric data!")

        # We have the problem, that we have a lot of dependencies, thats why we need to put classes, methods, enums,
        # interfaces, and methods together and sort them correctly so that we can store them without any problems
        self.logger.info("Parsing & storing classes, interfaces, enums, and methods metric data...")
        self.prepare_csv_files()
        self.store_java_data()
        self.logger.info("Finished parsing & storing classes, interfaces, enums, and methods metric data!")

    def get_parent_type(self, parent, artifact_type):
        mongo_names = {'class': {'stored_packages': 'packageId', 'stored_classes': 'parentClazzId',
                                 'stored_methods': 'methodId', 'stored_interfaces': 'interfaceId',
                                 'stored_enums': 'enumId'},
                       'interface': {'stored_packages': 'packageId', 'stored_classes': 'clazzId',
                                     'stored_methods': 'methodId', 'stored_interfaces': 'parentInterfaceId',
                                     'stored_enums': 'enumId'},
                       'enum': {'stored_packages': 'packageId', 'stored_classes': 'clazzId',
                                'stored_methods': 'methodId', 'stored_interfaces': 'interfaceId',
                                'stored_enums': 'parentEnumId'},
                       'method': {'stored_packages': 'packageId', 'stored_classes': 'clazzId',
                                  'stored_methods': 'parentMethodId', 'stored_interfaces': 'interfaceId',
                                  'stored_enums': 'enumId'}}
        rdata = False
        name = False

        for d in ['stored_packages', 'stored_classes', 'stored_methods', 'stored_interfaces', 'stored_enums']:
            if parent in getattr(self, d):
                rdata = getattr(self, d)[parent]
                name = mongo_names[artifact_type][d]
                break

        if not rdata or not name:
            raise Exception('Error determining state')

        return name, rdata

    def store_java_data(self):
        classes_csv_path = glob.glob(os.path.join(self.output_path, "all_temp.csv"))[0]
        with open(classes_csv_path) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                long_name = self.sanitize_long_name(row['Path'])
                metrics_dict = self.sanitize_metrics_dictionary(copy.deepcopy(row))

                dat = {'revisionHash': self.revisionHash, 'startLine': row['Line'],
                       'endLine': row['EndLine'], 'startColumn': row['Column'], 'endColumn': row['EndColumn'],
                       'metrics': metrics_dict, 'componentIds': [self.stored_components[row['Component']]]}

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
                        self.logger.error(e)

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
                        self.logger.error(e)

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
                        self.logger.error(e)

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
                        self.logger.error(e)

    def prepare_csv_files(self):
        all_csv_paths = {'class': glob.glob(os.path.join(self.output_path, "*-Class.csv"))[0],
                         'enum': glob.glob(os.path.join(self.output_path, "*-Enum.csv"))[0],
                         'interface':  glob.glob(os.path.join(self.output_path, "*-Interface.csv"))[0],
                         'method': glob.glob(os.path.join(self.output_path, "*-Method.csv"))[0]}

        all_csvs_together = []
        for name, path in all_csv_paths.items():
            with open(path) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row['type'] = name
                    row['sortKey'] = row['Parent'].strip('L')
                    all_csvs_together.append(row)
        sorted_csvs = sorted(all_csvs_together, key=lambda k: int(k['sortKey']))

        with open(os.path.join(self.output_path, "all_temp.csv"), 'w') as csvfile:
            fieldnames = ['ID', 'Name', 'LongName', 'Parent', 'Component', 'Path', 'Line', 'Column', 'EndLine',
                          'EndColumn', 'CC', 'CCL', 'CCO', 'CI', 'CLC', 'CLLC', 'LDC', 'LLDC', 'LCOM5', 'NL', 'NLE',
                          'WMC', 'CBO', 'CBOI', 'NII', 'NOI', 'RFC', 'AD', 'CD', 'CLOC', 'DLOC', 'PDA', 'PUA', 'TCD',
                          'TCLOC', 'DIT', 'NOA', 'NOC', 'NOD', 'NOP', 'LLOC', 'LOC', 'NA', 'NG', 'NLA', 'NLG',
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
                    if row['Parent'] in self.stored_packages and row['ID'] not in written_ids:
                        written_ids.append(row['ID'])
                        writer.writerow(row)

                    if row['Parent'] in written_ids and row['ID'] not in written_ids:
                        written_ids.append(row['ID'])
                        writer.writerow(row)

                    if len(written_ids) == len(sorted_csvs):
                        not_finished = False
