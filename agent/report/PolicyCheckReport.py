from airspeed import
import airspeed


class PolicyCheckReport:
    def __init__(self, result, build_name, build_number):
        self.build_number = build_number
        self.build_name = build_name
        self.result = result
        self.template_folder = "templates/"
        self.template_file = "policy-check.vm"
        self.css_file = "wss.css"
        self.max_bar_height = 50
        self.license_limit = 6
        self.other_license = "Other types"

    def generate(self, outputDir, pack, properties):
        engine = create_template_engine(properties)




def create_template_engine(properties):
    pass
