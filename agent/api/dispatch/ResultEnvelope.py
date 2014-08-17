import json
class ResultEnvelope:
    def __init__(self, envelope_version, status, message, data):
        self.data = data
        self.message = message
        self.status = status
        self.envelope_version = envelope_version

    def to_string(self):
        result = "ResultEnvelope \n" + "envelopeVersion= " + self.envelope_version + ","
        result += "\n status= " + self.status + ","
        result += "\n message= " + self.message + ","
        result += "\n data= " + self.data + "\n"
        return result


full_json = '{"envelopeVersion":"1.0", "status":1, "message":"ok", "data":"{\\"organization\\":\\"py try 43\\",\\"updatedProjects\\":[\\"ios3\\"],\\"createdProjects\\":[]}"}'
parsed_json = json.loads(full_json)
print "this is it: ", parsed_json
data_json = json.loads(parsed_json['data'])
print "data is: ", data_json