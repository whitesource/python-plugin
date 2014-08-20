import requests
import logging
import jsonpickle
from agent.api.dispatch.RequestType import RequestType
from agent.api.dispatch import ResultEnvelope
from agent.api.dispatch import UpdateInventoryResult
from agent.api.dispatch import CheckPoliciesResult


class WssServiceClient:
    """ Http request creation and execution (update/check_policies) """

    def __init__(self, service_url):
        self.service_url = service_url

    def to_string(self):
        result = "service url= " + self.service_url
        return result

    def update_inventory(self, update_request):
        """ Create update request """
        return self.service(update_request)

    def check_policies(self, policies_request):
        """ Create check policies request """
        return self.service(policies_request)

    def service(self, request):
        result = None
        headers = {'content-type': 'application/json'}
        request_params = self.create_http_request(request)

        logging.debug("The request params are: " + print_request_params(request_params))
        logging.debug("Sending the http request")

        try:
            # send http request
            response = requests.post(self.service_url, headers=headers, params=request_params)
            logging.debug("The response to the request is: " + response.text)

            try:
                # deal with response of the request
                result_envelope = ResultEnvelope.json_to_result_envelope(response.text)

                if request.request_type == RequestType.UPDATE:
                    result = UpdateInventoryResult.json_to_update_inventory(result_envelope.data)
                if request.request_type == RequestType.CHECK_POLICIES:
                    result = CheckPoliciesResult.json_to_check_policies(result_envelope.data)
            except Exception as err:
                print "Error parsing response", err.message

        except requests.RequestException as err:
            print "Unable to send http request", err.message

        return result

    def create_http_request(self, request):
        """ Create the actual http request to be sent to the agent """
        params_dict = None
        try:
            sent_request_json = jsonpickle.encode(request.projects, unpicklable=False)
            logging.debug("The request json is: " + sent_request_json)
            params_dict = {'type': request.request_type.__str__().split('.')[-1],
                           'agent': request.agent,
                           'agentVersion': request.agent_version,
                           'token': request.org_token,
                           'product': request.product,
                           'productVersion': request.product_version,
                           'timeStamp': request.time_stamp,
                           'diff': sent_request_json}
        except Exception as err:
            print "Not able to process request parameters", err.message
        return params_dict


def print_request_params(params):
    result = ''
    for key in params:
        result += str(params[key]) + "\n"
    return result