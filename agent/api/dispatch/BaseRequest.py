import time


class BaseRequest:
    """ The base request object, to be inherited by different request objects"""

    def __init__(self, org_token, product, product_version, req_type):
        self.requestType = req_type
        self.orgToken = org_token
        self.product = product
        self.productVersion = product_version
        self.timeStamp = str(int(time.time()))
        self.agent = 'generic'
        self.agentVersion = '1.0'

    def to_string(self):
        """ Prints the class instance """

        result = "UpdateInventoryRequest \n" + "request type= " + self.requestType + ","
        result += "\n org_token= " + self.orgToken + ","
        result += "\n product= " + self.product + ","
        result += "\n product_version= " + str(self.productVersion) + "\n"
        return result
