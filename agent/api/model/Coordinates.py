class Coordinates:
    """  WhiteSource model for artifact's coordinates. """

    def __init__(self, group_id, artifact_id, version_id):
        self.groupId = group_id
        self.artifactId = artifact_id
        self.versionId = version_id


def create_project_coordinates(distribution):
    """ Creates a 'Coordinates' instance for the user package"""

    dist_name = distribution.get_name()
    dist_version = distribution.get_version()
    coordinates = Coordinates(group_id=None, artifact_id=dist_name, version_id=dist_version)
    return coordinates