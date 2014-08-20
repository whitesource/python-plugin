import jsonpickle
import logging


class CheckPoliciesResult(object):
    """ Result of the check policies operation. """

    def __init__(self, organization, existing_projects, new_projects, projects_new_resources):
        self.projects_new_resources = projects_new_resources
        self.new_projects = new_projects
        self.existing_projects = existing_projects
        self.organization = organization

    def has_rejections(self):
        """ Returns True if some project in this result have some rejected dependency. """
        has_rejections = False
        index = 0
        roots = self.existing_projects.values() + self.new_projects.values()

        while (not has_rejections) and (index < len(roots)):
            has_rejections = roots.pop(index).has_rejections()

        return has_rejections


def json_to_check_policies(json):
    """ Converts json result from server into a CheckPoliciesResult"""

    try:
        json_dict = jsonpickle.decode(json)
        check_policies = CheckPoliciesResult(json_dict['organization'], json_dict['existingProjects'],
                                             json_dict['newProjects'], json_dict['projectNewResources'])
        logging.debug("The CheckPoliciesResult instance is ready")
        return check_policies
    except Exception as err:
        print "Unable to parse json to CheckPoliciesResult object", err.message
        raise
