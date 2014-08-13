from agent.dispatch.BaseRequest import BaseRequest

from agent.api.dispatch import RequestType


class UpdateInventoryRequest(BaseRequest):
    """ The update request, inherits from 'BaseRequest' """

    def __init__(self, org_token, product, product_version, projects=[]):
        BaseRequest.__init__(self, org_token=org_token, product=product, product_version=product_version,
                             req_type=RequestType.UPDATE)
        self.projects = projects
