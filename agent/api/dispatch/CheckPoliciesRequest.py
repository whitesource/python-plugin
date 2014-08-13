from agent.api.dispatch.BaseRequest import BaseRequest
from agent.api.dispatch.RequestType import RequestType


class CheckPoliciesRequest(BaseRequest):
    """ The check_policies request, inherits from 'BaseRequest' """

    def __init__(self, org_token, product, product_version, projects=[]):
        BaseRequest.__init__(self, org_token, product, product_version, RequestType.CHECK_POLICIES)
        self.projects = projects
