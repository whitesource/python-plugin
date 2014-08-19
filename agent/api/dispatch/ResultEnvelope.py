import jsonpickle


class ResultEnvelope(object):
    def __init__(self, envelope_version, status, message, data):
        self.data = data
        self.message = message
        self.status = status
        self.envelopeVersion = envelope_version

    def to_string(self):
        result = "ResultEnvelope \n" + "envelopeVersion= " + self.envelope_version + ","
        result += "\n status= " + self.status + ","
        result += "\n message= " + self.message + ","
        result += "\n data= " + self.data + "\n"
        return result


def json_to_result_envelope(json):
    """ Converts json result from server into a ResultEnvelope object"""
    json_dict = jsonpickle.decode(json)
    res_env = ResultEnvelope(json_dict['envelopeVersion'], json_dict['status'], json_dict['message'], json_dict['data'])
    return res_env
