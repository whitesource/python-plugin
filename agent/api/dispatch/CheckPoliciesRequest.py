from agent.api.dispatch.BaseRequest import BaseRequest
from agent.api.dispatch.RequestType import RequestType


class CheckPoliciesRequest(BaseRequest):
    """ The check_policies request, inherits from 'BaseRequest' """

    def __init__(self, org_token, user_key, product, product_version, projects=[], force_check_all_dependencies = False):
        BaseRequest.__init__(self, org_token, user_key, product, product_version, RequestType.CHECK_POLICY_COMPLIANCE)
        self.force_check_all_dependencies = force_check_all_dependencies
        self.projects = projects
