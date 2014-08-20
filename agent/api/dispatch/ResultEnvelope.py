import jsonpickle
import logging


class ResultEnvelope(object):
    def __init__(self, envelope_version, status, message, data):
        self.data = data
        self.message = message
        self.status = status
        self.envelopeVersion = envelope_version

    def to_string(self):
        result = "ResultEnvelope \n" + "envelopeVersion= " + self.envelopeVersion + ","
        result += "\nstatus= " + str(self.status) + ","
        result += "\nmessage= " + self.message + ","
        result += "\ndata= " + self.data + "\n"
        return result


def json_to_result_envelope(json):
    """ Converts json result from server into a ResultEnvelope object"""

    try:
        json_dict = jsonpickle.decode(json)
        res_env = ResultEnvelope(json_dict['envelopeVersion'], json_dict['status'], json_dict['message'], json_dict['data'])
        logging.debug("The resulted envelope is: " + res_env.to_string())
        return res_env
    except Exception as err:
        print "Unable to parse json response to ResultEnvelope object", err.message
        raise
