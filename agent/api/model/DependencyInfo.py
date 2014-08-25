class DependencyInfo:
    """ WhiteSource Model for a project's dependency """

    def __init__(self, group_id=None, artifact_id=None, version_id=None, dependency_type=None, sha1=None,
                 classifier=None, scope=None, system_path=None, optional=None, children=[], exclusions=[]):
        self.children = children
        self.optional = optional
        self.systemPath = system_path
        self.scope = scope
        self.classifier = classifier
        self.exclusions = exclusions
        self.sha1 = sha1
        self.dependencyType = dependency_type
        self.versionId = version_id
        self.groupId = group_id
        self.artifactId = artifact_id
