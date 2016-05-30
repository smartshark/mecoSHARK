from mecoshark.resultparser.sourcemeterparser import SourcemeterParser
import glob, os, csv, copy
from mecoshark.resultparser.mongomodels import Module, ModuleState, Function, FunctionState

class SourcemeterPythonParser(SourcemeterParser):

    def __init__(self, output_path, input_path, url, revisionHash):
        super().__init__(output_path, input_path, url, revisionHash)
        self.stored_modules = {}


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

        self.logger.info("Parsing & storing module metric data...")
        self.store_modules_csv()
        self.logger.info("Finished parsing & storing module metric data!")

        self.logger.info("Parsing & storing classes metric data...")
        self.store_classes_csv()
        self.logger.info("Finished parsing & storing classes metric data!")

        self.logger.info("Parsing & storing methods metric data...")
        self.store_methods_csv()
        self.logger.info("Finished parsing & storing methods metric data!")

        self.logger.info("Parsing & storing functions metric data...")
        self.store_functions_csv()
        self.logger.info("Finished parsing & storing functions metric data!")

    def store_modules_csv(self):
        modules_csv_path = glob.glob(os.path.join(self.output_path, "*-Module.csv"))[0]

        with open(modules_csv_path) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                sanitized_path = self.sanitize_long_name(row['Path'])
                module = Module.objects(projectId=self.projectid, fileId=self.stored_files[sanitized_path],
                                        name=row["Name"]) \
                    .upsert_one(projectId=self.projectid, fileId=self.stored_files[sanitized_path], name=row["Name"])
                self.stored_modules[row['ID']] = module.id

                metrics_dict = self.sanitize_metrics_dictionary(copy.deepcopy(row))

                ModuleState.objects(moduleId=module.id, revisionHash=self.revisionHash) \
                    .upsert_one(moduleId=module.id, revisionHash=self.revisionHash, metrics=metrics_dict,
                                startLine=row['Line'], endLine=row['EndLine'], startColumn=row['Column'],
                                endColumn=row['EndColumn'], packageId=self.stored_packages[row['Parent']],
                                componentId=self.stored_components[row['Component']])

    def get_parent_type(self, parent):
        mongo_names = {'stored_modules': 'moduleId', 'stored_functions': 'parentFunctionId',
                       'stored_methods': 'methodId'}
        rdata = False
        name = False

        for d in ['stored_modules', 'stored_functions', 'stored_methods']:
            if parent in getattr(self, d):
                rdata = getattr(self, d)[parent]
                name = mongo_names[d]
                break

        if not rdata or not name:
            raise Exception('Error determining state')

        return name, rdata

    def store_functions_csv(self):
        functions_csv_path = glob.glob(os.path.join(self.output_path, "*-Function.csv"))[0]
        with open(functions_csv_path) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                sanitized_path = self.sanitize_long_name(row['Path'])
                function = Function.objects(projectId=self.projectid, fileId=self.stored_files[sanitized_path],
                                            longName=row['LongName']) \
                    .upsert_one(projectId=self.projectid, fileId=self.stored_files[sanitized_path], name=row["Name"],
                                longName=row['LongName'])
                self.stored_functions[row['ID']] = function.id

                metrics_dict = self.sanitize_metrics_dictionary(copy.deepcopy(row))

                try:
                    dat = {'functionId': function.id, 'revisionHash': self.revisionHash, 'metrics': metrics_dict,
                           'startLine': row['Line'], 'endLine': row['EndLine'], 'startColumn': row['Column'],
                           'endColumn': row['EndColumn'], 'componentIds': [self.stored_components[row['Component']]]}
                    name, data = self.get_parent_type(row['Parent'])
                    dat[name] = data
                    FunctionState.objects(functionId=function.id, revisionHash=self.revisionHash)\
                         .upsert_one(**dat)
                except Exception as e:
                    self.logger.error(e)
