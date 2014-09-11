import requests
import logging
import jsonpickle
from agent.api.dispatch.RequestType import RequestType
from agent.api.dispatch import ResultEnvelope
from agent.api.dispatch import UpdateInventoryResult
from agent.api.dispatch import CheckPoliciesResult


class WssServiceClient:
    """ Http request creation and execution (update/check_policies) """

    def __init__(self, service_url, proxy_setting=None):
        self.proxySetting = proxy_setting
        self.serviceUrl = service_url

    def to_string(self):
        """ Prints the class instance """

        result = "service url= " + self.serviceUrl
        return result

    def update_inventory(self, update_request):
        """ Create update request """

        return self.service(update_request)

    def check_policies(self, policies_request):
        """ Create check policies request """

        return self.service(policies_request)

    def service(self, request):
        """ Sends http request and parses the response """

        proxy = None
        result = None
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        request_params = self.create_http_request(request)

        if self.proxySetting:
            proxy = self.create_proxy()

        logging.debug("The request params are:\n" + print_request_params(request_params))
        logging.debug("Sending the http request")

        try:
            # send http request
            response = requests.post(self.serviceUrl, headers=headers, data=request_params, proxies=proxy)
            logging.debug("The response to the request is: " + response.text)

            try:
                # deal with response of the request
                result_envelope = ResultEnvelope.json_to_result_envelope(response.text)

                if request.requestType == RequestType.UPDATE:
                    result = UpdateInventoryResult.json_to_update_inventory(result_envelope.data)
                if request.requestType == RequestType.CHECK_POLICIES:
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
            logging.debug("The request json is:\n" + sent_request_json)
            params_dict = {'type': request.requestType.__str__().split('.')[-1],
                           'agent': request.agent,
                           'agentVersion': request.agentVersion,
                           'token': request.orgToken,
                           'product': request.product,
                           'productVersion': request.productVersion,
                           'timeStamp': request.timeStamp,
                           'diff': sent_request_json}
        except Exception as err:
            print "Not able to process request parameters", err.message
        return params_dict

    def create_proxy(self):
        """ Create the proxy dict for the http request from the config file """

        proxy_dict = {}
        proxy_str = ""

        if ('ip' in self.proxySetting) and ('port' in self.proxySetting):
            if (self.proxySetting['ip'] != '') and (self.proxySetting['port'] != ''):
                if ('user' in self.proxySetting) and ('password' in self.proxySetting):
                    if (self.proxySetting['user'] != '') and (self.proxySetting['password'] != ''):
                        proxy_str += "http://" + self.proxySetting['user'] + ":" + self.proxySetting['password'] + "@"
                proxy_str += self.proxySetting['ip'] + ":" + self.proxySetting['port']
                proxy_dict['http'] = proxy_str

        return proxy_dict


def print_request_params(params):
    result = ''
    for key in params:
        result += key + ': ' + str(params[key]) + "\n"
    return result