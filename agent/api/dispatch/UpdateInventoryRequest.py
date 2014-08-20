from agent.api.dispatch.BaseRequest import BaseRequest
from agent.api.dispatch.RequestType import RequestType


class UpdateInventoryRequest(BaseRequest):
    """ The update request, inherits from 'BaseRequest' """

    def __init__(self, org_token, product, product_version, projects=[]):
        BaseRequest.__init__(self, org_token, product, product_version, RequestType.UPDATE)
        self.projects = projects

    def to_string(self):
        result = "UpdateInventoryRequest \n" + "request type= " + self.request_type + ","
        result += "\n org_token= " + self.org_token + ","
        result += "\n product= " + self.product + ","
        result += "\n product_version= " + str(self.product_version) + ","
        result += "\n projects= " + self.projects + "\n"
        return result
