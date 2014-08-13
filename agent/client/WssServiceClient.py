import requests

class WssServiceClient:
    """ Http request creation and execution (update/check_policies) """

    def __init__(self, request_json, service_url):
        self.service_url = service_url
        #not relevant
        #self.request_json = request_json

    def update_inventory(self, update_request):
        return self.service(update_request)

    def check_policies(self, policies_request):
        return self.service(policies_request)

    def service(self, request):
        headers = {'content-type': 'application/json'}
        request = requests.post(self.service_url, headers=headers, params=self.create_http_request(request))
        return request

    def create_http_request(self, request):
        # create json here not in WssPythonPlugin
        params_dict = {'type': request.request_type,
                       'agent': request.agent,
                       'agentVersion': request.agent_version,
                       'token': request.org_token,
                       'product': request.product,
                       'productVersion': request.product_version,
                       'timeStamp': request.time_stamp,
                       'diff': self.request_json}
        return params_dict



