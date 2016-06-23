from mongoengine import Document, StringField, DateTimeField, ListField, DateTimeField, IntField, BooleanField, \
    ObjectIdField, DictField, DecimalField


class File(Document):
    """ Document that inherits from :class:`mongoengine.Document`. Holds information for the file collection.
    
    :property projectId: id of the project, which belongs to the file action (type: :class:`mongoengine.fields.ObjectIdField`)
    :property path: path of the file (type: :class:`mongoengine.fields.StringField`)
    :property name: name of the file (type: :class:`mongoengine.fields.StringField`)
    
    .. NOTE:: Unique (or primary key) are the fields: path, name, and projectId.
    """
    
    #PK path, name, projectId
    projectId = ObjectIdField(required=True,unique_with=['path'] )
    path = StringField(max_length=300, required=True,unique_with=['projectId'])
    name = StringField(max_length=100, required=True)


class Project(Document):
    """ Document that inherits from :class:`mongoengine.Document`. Holds information for the project collection.
    
    :property url: url to the project repository (type: :class:`mongoengine.fields.StringField`)
    :property name: name of the project (type: :class:`mongoengine.fields.StringField`)
    :property repositoryType: type of the repository (type: :class:`mongoengine.fields.StringField`)
    
    .. NOTE:: Unique (or primary key) is the field url.
    """
    # PK uri
    url = StringField(max_length=400, required=True, unique=True)
    name = StringField(max_length=100, required=True)
    repositoryType = StringField(max_length=15)


class FileState(Document):
    """ Document that inherits from :class:`mongoengine.Document`. Holds information for the file_state collection.

    :property file_id: id of the file to which the state belongs (type: :class:`mongoengine.fields.ObjectIdField`)
    :property revision_hash: revision_hash to which the state belongs (type: :class:`mongoengine.fields.StringField`)
    :property long_name: long_name of the state entity (e.g., pyvcssharhk.main.py) (type: :class:`mongoengine.fields.StringField`)
    :property component_ids: component_ids to which this entity belongs (type: :class:`mongoengine.fields.ListField` of :class:`mongoengine.fields.ObjectFieldId`)
    :property name: name of the state entity (type: :class:`mongoengine.fields.StringField`)
    :property file_type: file_type of the state entity (e.g., class, attribute, method, function, ...) (type: :class:`mongoengine.fields.StringField`)
    :property parent: parent of the state entity (e.g., if the entity is a method, the parent can be a class) (type: :class:`mongoengine.fields.ObjectFieldId`)
    :property metrics: metrics of the state entity (type: :class:`mongoengine.fields.DictField`)

    .. NOTE:: Unique (or primary keys) are the fields revision_hash, long_name, and file_id.
    """
    file_id = ObjectIdField(required=True,unique_with=['revision_hash', 'long_name'])
    revision_hash = StringField(max_length=50, required=True, unique_with=['file_id', 'long_name'])
    long_name = StringField(required=True, unique_with=['file_id', 'revision_hash'])
    component_ids = ListField(ObjectIdField())
    name = StringField()
    file_type = StringField(required=True)
    parent = ObjectIdField()
    metrics = DictField()


class MetaPackageState(Document):
    """ Document that inherits from :class:`mongoengine.Document`. Holds information for the meta_package_state collection.
    Here information about a collection of file_states is saved (e.g. packages) that do not belong to one file, but
    have associations to more than one file.

    :property project_id: id of the project to which this meta package state belongs (type: :class:`mongoengine.fields.ObjectIdField`)
    :property long_name: long_name of the state entity (type: :class:`mongoengine.fields.StringField`)
    :property revision_hash: revision_hash to which the state belongs (type: :class:`mongoengine.fields.StringField`)
    :property name: name of the state entity (type: :class:`mongoengine.fields.StringField`)
    :property component_ids: component_ids of the state entity (e.g., pyvcssharhk.main.py) (type: :class:`mongoengine.fields.StringField`)
    :property parent_state: parent of the state entity  (type: :class:`mongoengine.fields.ObjectFieldId`)
    :property metrics: metrics of the state entity (type: :class:`mongoengine.fields.DictField`)

    .. NOTE:: Unique (or primary keys) are the fields revision_hash, long_name, and project_id.
    """
    project_id = ObjectIdField(required=True, unique_with=['long_name', 'revision_hash'])
    long_name = StringField(require=True, unique_with=['project_id', 'revision_hash'])
    revision_hash = StringField(max_length=50, required=True, unique_with=['project_id', 'long_name'])
    name = StringField()
    component_ids = ListField(ObjectIdField())
    parent_state = ObjectIdField()
    metrics = DictField()


class CloneInstance(Document):
    """ Document that inherits from :class:`mongoengine.Document`. Holds information for the clone_instance collection.

    :property project_id: id of the project to which this meta package state belongs (type: :class:`mongoengine.fields.ObjectIdField`)
    :property name: name of the clone entity (type: :class:`mongoengine.fields.StringField`)
    :property revision_hash: revision_hash to which the state belongs (type: :class:`mongoengine.fields.StringField`)
    :property fileId: id of the file to which the clone belongs (type: :class:`mongoengine.fields.ObjectIdField`)
    :property cloneClass: name of the clone class  (type: :class:`mongoengine.fields.StringField`)
    :property cloneClassMetrics: metrics of the clone class (type: :class:`mongoengine.fields.DictField`)
    :property cloneInstanceMetrics: metrics of the clone class (type: :class:`mongoengine.fields.DictField`)
    :property startLine: start line of the clone (type: :class:`mongoengine.fields.IntField`)
    :property endLine: end line of the clone (type: :class:`mongoengine.fields.IntField`)
    :property startColumn: start column of the clone (type: :class:`mongoengine.fields.IntField`)
    :property endColumn: end column of the clone (type: :class:`mongoengine.fields.IntField`)

    .. NOTE:: Unique (or primary keys) are the fields revisionHash, name, and projectId.
    """

    projectId = ObjectIdField(required=True, unique_with=['name', 'revisionHash'])
    name = StringField(required=True, unique_with=['projectId', 'revisionHash'])
    revisionHash = StringField(max_length=50, required=True, unique_with=['projectId', 'name'])
    fileId = ObjectIdField(required=True)
    cloneClass = StringField(required=True)
    cloneClassMetrics = DictField(required=True)
    cloneInstanceMetrics = DictField(required=True)
    startLine = IntField(required=True)
    endLine = IntField(required=True)
    startColumn = IntField(required=True)
    endColumn = IntField(required=True)



