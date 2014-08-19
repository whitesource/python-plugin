import requests
import json


class WssServiceClient:
    """ Http request creation and execution (update/check_policies) """

    def __init__(self, service_url):
        self.service_url = service_url

    def update_inventory(self, update_request, debuging):
        """ Create update request"""
        return self.service(update_request, debuging)

    def check_policies(self, policies_request):
        """ Create check policies request"""
        return self.service(policies_request)

    def service(self, request, debuging):
        headers = {'content-type': 'application/json'}
        params_dict = self.create_http_request(request)
        if debuging == 'y':
            print "The request is:\n"
            for key in params_dict:
                print key + ": ", params_dict[key]
        request = requests.post(self.service_url, headers=headers, params=params_dict)
        if debuging == 'y':
            print "the request result is: ", request.text
        return request

    def create_http_request(self, request):
        """ Create the actual http request to be sent to the agent"""
        sent_request_json = self.create_request_json(request)
        params_dict = {'type': request.request_type.__str__().split('.')[-1],
                       'agent': request.agent,
                       'agentVersion': request.agent_version,
                       'token': request.org_token,
                       'product': request.product,
                       'productVersion': request.product_version,
                       'timeStamp': request.time_stamp,
                       'diff': sent_request_json}
        return params_dict

    @staticmethod
    def create_request_json(request):
        """ Creates a json out of a request"""

        def object_to_json(obj):
            return obj.__dict__

        project_info_json = json.dumps(request.projects, default=object_to_json, sort_keys=True, indent=4,
                                       separators=(',', ': '))
        return project_info_json



