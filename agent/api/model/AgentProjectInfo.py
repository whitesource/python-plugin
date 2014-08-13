__author__ = 'Yossi Weinberg'


class AgentProjectInfo:
    """ Class to hold all information about a project to update. """

    def __init__(self, coordinates, dependencies=None, parent_coordinates=None, project_token=None):
        self.coordinates = coordinates
        self.dependencies = dependencies
        self.parent_coordinates = parent_coordinates
        self.projectToken = project_token


# coordinate = Coordinates('wss', 'py_plugin', '0.1')
# dep1 = DependencyInfo('apache', 'spring', '0.2', sha1='100')
# dep2 = DependencyInfo('google', 'chrome', '0.3', sha1='200')
# dep3 = DependencyInfo('mozilla', 'firefox', '0.4', sha1='300')
# project_dep = [dep1, dep2, dep3]
#
# project_info = AgentProjectInfo(coordinate, dependencies=project_dep)
#
#
# def object_to_json(object):
#     return object.__dict__
#
# new_json = json.dumps([project_info], default=object_to_json, sort_keys=True, indent=4, separators=(',', ': '))
# print "To json: \n:", new_json
# requestFactory = WssServiceClient("http://localhost/agent", new_json)
# new_request = requestFactory.create_request()
# #print new_request.text
