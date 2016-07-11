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

    :property commit_id: id of the commit to which the file state belongs to (type: :class:`mongoengine.fields.ObjectIdField`)
    :property file_id: id of the file to which the state belongs (type: :class:`mongoengine.fields.ObjectIdField`)
    :property long_name: long_name of the state entity (e.g., pyvcssharhk.main.py) (type: :class:`mongoengine.fields.StringField`)
    :property component_ids: component_ids to which this entity belongs (type: :class:`mongoengine.fields.ListField` of :class:`mongoengine.fields.ObjectFieldId`)
    :property name: name of the state entity (type: :class:`mongoengine.fields.StringField`)
    :property file_type: file_type of the state entity (e.g., class, attribute, method, function, ...) (type: :class:`mongoengine.fields.StringField`)
    :property parent: parent of the state entity (e.g., if the entity is a method, the parent can be a class) (type: :class:`mongoengine.fields.ObjectFieldId`)
    :property metrics: metrics of the state entity (type: :class:`mongoengine.fields.DictField`)

    .. NOTE:: Unique (or primary keys) are the fields commit_id and file_id.
    """
    file_id = ObjectIdField(required=True,unique_with=['commit_id', 'long_name'])
    commit_id = ObjectIdField(required=True, unique_with=['file_id', 'long_name'])
    long_name = StringField(required=True, unique_with=['file_id', 'commit_id'])
    component_ids = ListField(ObjectIdField())
    name = StringField()
    file_type = StringField()
    parent = ObjectIdField()
    metrics = DictField()


class MetaPackageState(Document):
    """ Document that inherits from :class:`mongoengine.Document`. Holds information for the meta_package_state collection.
    Here information about a collection of file_states is saved (e.g. packages) that do not belong to one file, but
    have associations to more than one file.

    :property commit_id: id of the commit to which the meta package state belongs (type: :class:`mongoengine.fields.ObjectIdField`)
    :property long_name: long_name of the state entity (type: :class:`mongoengine.fields.StringField`)
    :property name: name of the state entity (type: :class:`mongoengine.fields.StringField`)
    :property component_ids: component_ids of the state entity (e.g., pyvcssharhk.main.py) (type: :class:`mongoengine.fields.StringField`)
    :property parent_state: parent of the state entity  (type: :class:`mongoengine.fields.ObjectFieldId`)
    :property metrics: metrics of the state entity (type: :class:`mongoengine.fields.DictField`)

    .. NOTE:: Unique (or primary keys) are the fields commit_id and long_name.
    """
    commit_id = ObjectIdField(required=True, unique_with=['long_name'])
    long_name = StringField(require=True, unique_with=['commit_id'])
    name = StringField()
    component_ids = ListField(ObjectIdField())
    parent_state = ObjectIdField()
    metrics = DictField()


class CloneInstance(Document):
    """ Document that inherits from :class:`mongoengine.Document`. Holds information for the clone_instance collection.

    :property commit_id: id of the commit, where the clone was detected (type: :class:`mongoengine.fields.ObjectIdField`)
    :property name: name of the clone entity (type: :class:`mongoengine.fields.StringField`)
    :property fileId: id of the file to which the clone belongs (type: :class:`mongoengine.fields.ObjectIdField`)
    :property cloneClass: name of the clone class  (type: :class:`mongoengine.fields.StringField`)
    :property cloneClassMetrics: metrics of the clone class (type: :class:`mongoengine.fields.DictField`)
    :property cloneInstanceMetrics: metrics of the clone class (type: :class:`mongoengine.fields.DictField`)
    :property startLine: start line of the clone (type: :class:`mongoengine.fields.IntField`)
    :property endLine: end line of the clone (type: :class:`mongoengine.fields.IntField`)
    :property startColumn: start column of the clone (type: :class:`mongoengine.fields.IntField`)
    :property endColumn: end column of the clone (type: :class:`mongoengine.fields.IntField`)

    .. NOTE:: Unique (or primary keys) are the fields commit_id, name, and fileId.
    """

    commit_id = ObjectIdField(required=True, unique_with=['name', 'fileId'])
    name = StringField(required=True, unique_with=['commit_id', 'fileId'])
    fileId = ObjectIdField(required=True, unique_with=['commit_id', 'name'])
    cloneClass = StringField(required=True)
    cloneClassMetrics = DictField(required=True)
    cloneInstanceMetrics = DictField(required=True)
    startLine = IntField(required=True)
    endLine = IntField(required=True)
    startColumn = IntField(required=True)
    endColumn = IntField(required=True)


class Commit(Document):
    """ Document that inherits from :class:`mongoengine.Document`. Holds information for the commit collection.

    :property projectId: id of the project, which belongs to the file action (type: :class:`mongoengine.fields.ObjectIdField`)
    :property revisionHash: revision hash of the commit (type: :class:`mongoengine.fields.StringField`)
    :property branches: list of branches to which the commit belongs to (type: :class:`mongoengine.fields.ListField(:class:`mongoengine.fields.StringField`)`)
    :property tagIds: list of tag ids, which belong to the commit (type: :class:`mongoengine.fields.ListField(:class:`mongoengine.fields.ObjectIdField`)`)
    :property parents: list of parents of the commit (type: :class:`mongoengine.fields.ListField(:class:`mongoengine.fields.StringField`)`)
    :property authorId: id of the author of the commit (type: :class:`mongoengine.fields.ObjectIdField`)
    :property authorDate: date when the commit was created (type: :class:`mongoengine.fields.DateTimeField`)
    :property authorOffset: offset of the authorDate (type: :class:`mongoengine.fields.IntField`)
    :property committerId: id of the committer of the commit (type: :class:`mongoengine.fields.ObjectIdField`)
    :property committerDate: date when the commit was committed (type: :class:`mongoengine.fields.DateTimeField`)
    :property committerOffset: offset of the committerDate (type: :class:`mongoengine.fields.IntField`)
    :property message: commit message (type: :class:`mongoengine.fields.StringField`)
    :property fileActionIds: list of file action ids, which belong to the commit (type: :class:`mongoengine.fields.ListField(:class:`mongoengine.fields.ObjectIdField`)`)

    .. NOTE:: Unique (or primary key) are the fields projectId and revisionHash.
    """

    #PK: projectId and revisionhash
    projectId = ObjectIdField(required=True,unique_with=['revisionHash'] )
    revisionHash = StringField(max_length=50, required=True, unique_with=['projectId'])
    branches = ListField(StringField(max_length=100))
    tagIds = ListField(ObjectIdField())
    parents = ListField(StringField(max_length=50))
    authorId = ObjectIdField()
    authorDate = DateTimeField()
    authorOffset = IntField()
    committerId = ObjectIdField()
    committerDate = DateTimeField()
    committerOffset = IntField()
    message = StringField()
    fileActionIds = ListField(ObjectIdField())


    def __str__(self):
        return ""



