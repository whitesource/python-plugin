from agent.dispatch.BaseRequest import BaseRequest

from agent.api.dispatch import RequestType


class CheckPoliciesRequest(BaseRequest):
    """ The check_policies request, inherits from 'BaseRequest' """

    def __init__(self, org_token, product, product_version, projects=[]):
        BaseRequest.__init__(org_token, product, product_version, req_type=RequestType.CHECK_POLICIES)
        self.projects = projects
