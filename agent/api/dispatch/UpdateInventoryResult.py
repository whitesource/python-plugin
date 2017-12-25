import jsonpickle
import logging


class UpdateInventoryResult(object):
    def __init__(self, organization, updated_projects, created_projects):
        self.organization = organization
        self.createdProjects = created_projects
        self.updatedProjects = updated_projects


def json_to_update_inventory(json):
    """ Converts json result from server into a UpdateInventoryResult"""

    try:
        json_dict = jsonpickle.decode(json)
        update_inventory = UpdateInventoryResult(json_dict['organization'], json_dict['updatedProjects'],
                                                 json_dict['createdProjects'])
        logging.debug("The UpdateInventoryResult instance is ready")
        return update_inventory
    except Exception as err:
        print json
        print("Unable to parse json to UpdateInventoryResult object", err.message)
        raise




