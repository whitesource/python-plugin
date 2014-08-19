import jsonpickle
from agent.api.dispatch.ResultEnvelope import ResultEnvelope


class UpdateInventoryResult(object):

    def __init__(self, organization, updated_projects, created_projects):
        self.organization = organization
        self.created_projects = created_projects
        self.updated_projects = updated_projects


def json_to_update_inventory(json):
    """ Converts json result from server into a UpdateInventoryResult"""
    json_dict = jsonpickle.decode(json)
    update_inventory= UpdateInventoryResult(json_dict['organization'], json_dict['createdProjects'], json_dict['updatedProjects'])
    return update_inventory


