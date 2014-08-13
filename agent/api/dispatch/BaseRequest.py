import time


class BaseRequest:
    """ The base request object, to be inherited by different request objects"""

    def __init__(self, org_token, product, product_version, req_type):
        self.request_type = req_type
        self.org_token = org_token
        self.product = product
        self.product_version = product_version
        self.time_stamp = str(int(time.time()))
        self.agent = 'generic'
        self.agent_version = '1.0'
