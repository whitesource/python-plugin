from agent.api.dispatch.BaseRequest import BaseRequest
from agent.api.dispatch.RequestType import RequestType


class UpdateInventoryRequest(BaseRequest):
    """ The update request, inherits from 'BaseRequest' """

    def __init__(self, org_token, user_key, product, product_version, projects=[]):
        BaseRequest.__init__(self, org_token, user_key, product, product_version, RequestType.UPDATE)
        self.projects = projects


