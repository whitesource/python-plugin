__author__ = 'Yossi Weinberg'


class AgentProjectInfo:
    """ Holding all information about a project. """

    def __init__(self, coordinates, dependencies=None, parent_coordinates=None, project_token=None):
        self.coordinates = coordinates
        self.dependencies = dependencies
        self.parent_coordinates = parent_coordinates
        self.projectToken = project_token