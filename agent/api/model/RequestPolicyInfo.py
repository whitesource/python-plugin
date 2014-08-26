class RequestPolicyInfo:
    def __init__(self, display_name=None, filter_type=None, filter_logic=None, action_type=None, action_logic=None,
                 project_level=None):
        self.projectLevel = project_level
        self.actionLogic = action_logic
        self.actionType = action_type
        self.filterLogic = filter_logic
        self.filterType = filter_type
        self.displayName = display_name


def from_dict(info_dict):
    """ Creates a RequestPolicyInfo object from a dict """

    policy_info = RequestPolicyInfo()

    if 'displayName' in info_dict:
        policy_info.displayName = info_dict['displayName']

    if 'filterType' in info_dict:
        policy_info.filterType = info_dict['filterType']

    if 'filterLogic' in info_dict:
        policy_info.filterLogic = info_dict['filterLogic']

    if 'actionType' in info_dict:
        policy_info.actionType = info_dict['actionType']

    if 'actionLogic' in info_dict:
        policy_info.actionLogic = info_dict['actionLogic']

    if 'projectLevel' in info_dict:
        policy_info.projectLevel = info_dict['projectLevel']

    return policy_info



