import requests
import json
import jsonpickle
from agent.api.dispatch.RequestType import RequestType
from agent.api.dispatch import ResultEnvelope
from agent.api.dispatch import UpdateInventoryResult


class WssServiceClient:
    """ Http request creation and execution (update/check_policies) """

    def __init__(self, service_url):
        self.service_url = service_url

    def update_inventory(self, update_request):
        """ Create update request """
        return self.service(update_request)

    def check_policies(self, policies_request):
        """ Create check policies request """
        return self.service(policies_request)

    def service(self, request):
        result = None
        headers = {'content-type': 'application/json'}
        response = requests.post(self.service_url, headers=headers, params=self.create_http_request(request))
        result_envelope = ResultEnvelope.json_to_result_envelope(response.text)

        if request.request_type == RequestType.UPDATE:
            result = UpdateInventoryResult.json_to_update_inventory(result_envelope.data)
        if request.request_type == RequestType.CHECK_POLICIES:
            pass
        # Todo: create policies check result object

        return result

    def create_http_request(self, request):
        """ Create the actual http request to be sent to the agent """
        sent_request_json = jsonpickle.encode(request.projects, unpicklable=False)
        params_dict = {'type': request.request_type.__str__().split('.')[-1],
                       'agent': request.agent,
                       'agentVersion': request.agent_version,
                       'token': request.org_token,
                       'product': request.product,
                       'productVersion': request.product_version,
                       'timeStamp': request.time_stamp,
                       'diff': sent_request_json}
        return params_dict
