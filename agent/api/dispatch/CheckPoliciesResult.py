import jsonpickle
import logging
import agent.api.model.PolicyCheckResourceNode as PolicyCheckResourceNode
import agent.api.model.ResourceInfo as ResourceInfo


class CheckPoliciesResult(object):
    """ Result of the check policies operation. """

    def __init__(self, organization, existing_projects=None, new_projects=None, projects_new_resources=None):
        if existing_projects is None:
            self.existingProjects = {}
        else:
            self.existingProjects = existing_projects

        if new_projects is None:
            self.newProjects = {}
        else:
            self.newProjects = new_projects

        if projects_new_resources is None:
            self.projectsNewResources = {}
        else:
            self.projectsNewResources = projects_new_resources

        self.projectsNewResources = projects_new_resources
        self.newProjects = new_projects
        self.existingProjects = existing_projects
        self.organization = organization

    def has_rejections(self):
        """ Returns True if some project in this result have some rejected dependency. """

        has_rejections = False
        index = 0
        roots = list(self.existingProjects.values()) + list(self.newProjects.values())

        while (not has_rejections) and (index < len(roots)):
            has_rejections = roots.pop(index).has_rejections()
            index += 1

        return has_rejections


def json_to_check_policies(json):
    """ Converts json result from server into a CheckPoliciesResult"""

    try:
        json_dict = jsonpickle.decode(json)
        check_policies = CheckPoliciesResult(json_dict['organization'],
                                             from_dict_to_resource_node(json_dict['existingProjects']),
                                             from_dict_to_resource_node(json_dict['newProjects']),
                                             from_dict_to_resource_infos(json_dict['projectNewResources']))
        logging.debug("The CheckPoliciesResult instance is ready")
        return check_policies
    except Exception as err:
        print("Unable to parse json to CheckPoliciesResult object", err.message)
        raise


def from_dict_to_resource_node(projects):
    """ Creates a ResourceNode object from a project dict """

    node_projects = {}
    for key, node in projects.items():
        node_projects[key] = PolicyCheckResourceNode.from_dict(node)

    return node_projects


def from_dict_to_resource_infos(projects):
    """ Creates a ResourceInfo object from a project dict """

    info_dict = {}
    for key, resources_dict_list in projects.items():
        resources = []
        for resource_dict in resources_dict_list:
            resources.append(ResourceInfo.from_dict(resource_dict))

        info_dict[key] = resources

    return info_dict
