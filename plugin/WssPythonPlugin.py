import imp
import importlib
from collections import defaultdict
import sys
import shutil
import tempfile
import hashlib
import logging
import jsonpickle
import errno
from distutils.sysconfig import get_python_lib

#WSE-402 add support for pip 9 and pip 10
try:
    from pip._internal.req import parse_requirements
except ImportError:
    from pip.req import parse_requirements


import pkg_resources as pk_res
from setuptools import Command
from setuptools.package_index import PackageIndex, os
from agent.api.model import PolicyCheckResourceNode

from agent.api.model.AgentProjectInfo import AgentProjectInfo
from agent.api.model import Coordinates
from agent.api.model.DependencyInfo import DependencyInfo
from agent.api.dispatch.UpdateInventoryRequest import UpdateInventoryRequest
from agent.api.dispatch.CheckPoliciesRequest import CheckPoliciesRequest
from agent.client.WssServiceClient import WssServiceClient

SPACE = " "

REQUIREMENTS = "-r"

UPDATE_REQUEST_FILE = "whitesource/update_request.json"

DASH = "-"


class SetupToolsCommand(Command):
    """setuptools Command"""
    description = "Setuptools WSS plugin"

    user_options = [
        ('offline=', 'o', 'Offline flag'),
        ('pathConfig=', 'p', 'Configuration file path'),
        ('debug=', 'd', 'Show debugging output'),
    ]

    def initialize_options(self):
        self.offline = None
        self.debug = None
        self.proxySetting = None
        self.service = None
        self.configDict = None
        self.pathConfig = None
        self.token = None
        self.userEnvironment = None
        self.distDepend = None
        self.pkgIndex = PackageIndex()
        self.dependencyList = []
        self.projectCoordinates = None
        self.tmpdir = tempfile.mkdtemp(prefix="wss_python_plugin-")

    def finalize_options(self):
        # log file activation and config
        if self.debug == 'y':
            logging.basicConfig(format='%(asctime)s%(levelname)s:%(message)s', level=logging.DEBUG,
                                filename='wss_plugin.log')

        # load and import config file
        try:
            sys.path.append(self.pathConfig)
            if sys.version_info.major >= 3:
                config_file_spec = importlib.util.spec_from_file_location('config_file', self.pathConfig)
                config_file_module = importlib.util.module_from_spec(config_file_spec)
                config_file_spec.loader.exec_module(config_file_module)
                self.configDict = config_file_module.config_info
            else:
                self.configDict = imp.load_source('config_file', self.pathConfig).config_info
            logging.info('Loading config_file was successful')
        except Exception as err:
            print("Can't import the config file.")
            sys.exit(err)

        # load proxy setting if exist
        if 'proxy' in self.configDict:
            self.proxySetting = self.configDict['proxy']
        if 'index_url' in self.configDict:
            self.pkgIndex = PackageIndex(index_url=self.configDict['index_url'])

        self.projectCoordinates = Coordinates.create_project_coordinates(self.distribution)
        self.userEnvironment = pk_res.Environment(get_python_lib(), platform=None, python=None)
        distribution_specification = self.distribution.get_name() + "==" + self.distribution.get_version()
        distribution_requirement = pk_res.Requirement.parse(distribution_specification)

        # resolve all dependencies
        try:
            self.distDepend = pk_res.working_set.resolve([distribution_requirement], env=self.userEnvironment)
            self.distDepend.pop(0)
            logging.info("Finished resolving dependencies")
        except Exception as err:
            print("distribution was not found on this system, and is required by this application", err.message)

    def run(self):
        self.validate_config_file()
        self.scan_modules()
        self.create_service()
        self.run_plugin()

    def validate_config_file(self):
        """ Validate content of config file params """

        # org token
        if 'org_token' in self.configDict:
            if self.configDict['org_token'] == '':
                sys.exit("Organization token is empty")
        else:
            sys.exit("No organization token option exists")

        logging.info("Validation of config file was successful")
        # Todo: check existence of other keys in dict

    def scan_modules(self):
        """ Downloads all the dependencies calculates their sha1 and creates a list of dependencies info"""

        if self.distDepend is not None:
            for dist in self.distDepend:
                try:
                    # create a dist instance from requirement instance
                    current_requirement = dist.as_requirement()
                    current_distribution = self.pkgIndex.fetch_distribution(
                        current_requirement, self.tmpdir, force_scan=True, source=True, develop_ok=True)

                    # create dep. root
                    if current_distribution is not None:
                        self.dependencyList.append(create_dependency_record(current_distribution))

                except Exception as err:
                    print("Error in fetching dists " + dist.key + " " + dist.version)
            logging.info("Finished calculation for all dependencies")
        else:
            logging.info("No dependencies were found")

        shutil.rmtree(self.tmpdir)

    def create_service(self):
        """ Creates a WssServiceClient with the destination url"""

        if ('url_destination' in self.configDict) and (self.configDict['url_destination'] != ''):
            self.service = WssServiceClient(self.configDict['url_destination'], self.proxySetting)
        else:
            self.service = WssServiceClient("https://saas.whitesourcesoftware.com/agent", self.proxySetting)

        logging.debug("The destination url is set to: " + self.service.to_string())

    def run_plugin(self):
        """ Initializes the plugin requests"""

        org_token = self.configDict['org_token']
        project = self.create_project_obj()
        product = ''
        product_version = ''

        self.policy_violation = False

        if 'product_name' in self.configDict:
            product = self.configDict['product_name']

        if 'product_version' in self.configDict:
            product_version = self.configDict['product_version']

        if self.configDict.get('offline') or self.offline:
            logging.debug("Offline request")
            offline_request(project, org_token, product, product_version)
        else:
            if self.configDict.get('check_policies'):
                logging.debug("Checking policies")
                self.check_policies(project, org_token, product, product_version)

            # no policy violations => send update and pass build
            if not self.policy_violation:
                logging.debug("Updating inventory")
                self.update_inventory(project, org_token, product, product_version)

            # policy violation AND force_update
            elif self.configDict.get('force_update'):
                print("However all dependencies will be force updated to project inventory.")
                logging.debug("Updating inventory")
                self.update_inventory(project, org_token, product, product_version)
                # fail the build
                if self.configDict.get('fail_on_error'):
                    print("Build failure due to policy violation (fail_on_error = True)")
                    sys.exit(1)

            # policy violation AND (NOT force_update)
            elif self.configDict.get('fail_on_error'):
                # fail the build
                print("Build failure due to policy violation (fail_on_error = True)")
                sys.exit(1)

    def create_project_obj(self):
        """ create the actual project """

        project_token = None
        if 'project_token' in self.configDict:
            project_token = self.configDict['project_token']
            if project_token == '':
                project_token = None

        return AgentProjectInfo(coordinates=self.projectCoordinates, dependencies=self.dependencyList,
                                project_token=project_token)

    def check_policies(self, project_info, token, product_name, product_version):
        """ Sends the check policies request to the agent according to the request type """

        projects = [project_info]

        force_check_all_dependencies = self.configDict.get('force_check_all_dependencies')
        request = CheckPoliciesRequest(token, product_name, product_version, projects, force_check_all_dependencies)

        result = self.service.check_policies(request)

        try:
            self.handle_policies_result(result)
        except Exception:
            logging.warning("Some dependencies do not conform with open source policies")
            sys.exit(1)

    def handle_policies_result(self, result):
        """ Checks if any policies rejected if so stops """

        logging.debug("Creating policies report")
        if result.has_rejections():
            self.policy_violation = True
            print("Some dependencies do not conform with open source policies:")
            print_policies_rejection(result)
        else:
            logging.debug("All dependencies conform with open source policies!")

    def update_inventory(self, project_info, token, product_name, product_version):
        """ Sends the update request to the agent according to the request type """

        logging.debug("Updating White Source")

        projects = [project_info]
        request = UpdateInventoryRequest(token, product_name, product_version, projects)
        result = self.service.update_inventory(request)
        print_update_result(result)


def calc_hash(file_for_calculation):
    """ Calculates sha1 of given file, src distribution in this case"""

    block_size = 65536
    hash_calculator = hashlib.sha1()
    with open(file_for_calculation, 'rb') as dependency_file:
        buf = dependency_file.read(block_size)
        while len(buf) > 0:
            hash_calculator.update(buf)
            buf = dependency_file.read(block_size)
    return hash_calculator.hexdigest()


def create_dependency_record(distribution):
    """ Creates a 'DependencyInfo' instance for package dependency"""

    dist_group = distribution.key
    if os.name == 'nt':
        dist_artifact = distribution.location.split('\\')[-1]
    else:
        dist_artifact = distribution.location.split('/')[-1]
    dist_version = distribution.version
    dist_sha1 = calc_hash(distribution.location)
    dependency = DependencyInfo(group_id=dist_group, artifact_id=dist_artifact, version_id=dist_version, sha1=dist_sha1)
    return dependency


def print_policies_rejection(result):
    """ Prints the result of the check policies result"""

    if result is not None:
        projects_dict = {}

        if result.newProjects:
            projects_dict.update(create_policy_dict(result.newProjects.items()))
        if result.existingProjects:
            projects_dict.update(create_policy_dict(result.existingProjects.items()))

        if bool(projects_dict):
            print(print_project_policies_rejection(projects_dict))
    else:
        print("There was a problem with the check policies result")
        logging.debug("The check policies result is empty")


def print_project_policies_rejection(policy_dict):
    """ Prints the the policy and corresponding rejected resources from projects"""
    output = ''

    for policy in policy_dict:
        # policy
        output += "Rejected by Policy " + '"' + policy + '":\n'
        for node in policy_dict[policy]:
            # name
            output += "\t* " + node.resource.displayName

            # licenses
            licenses = node.resource.licenses
            if licenses is not None:
                license_output = " ("
                for lice in licenses:
                    license_output += lice + ", "
                output += license_output[:-2] + ") \n"
    return output


def create_policy_dict(projects):
    """ Creates a dict of policies and the rejected libs by them"""

    policy_dict = defaultdict(list)

    # project iterator
    for project, resource_node in projects:
        rejected_node = PolicyCheckResourceNode.find_rejected_node(resource_node)

        # rejected node iterator
        for node in rejected_node:
            policy_dict[node.policy.displayName].append(node)

    return policy_dict


def print_update_result(result):
    """ Prints the result of the update result"""
    if result is not None:
        output = "White Source update results: \n"
        output += "White Source organization: " + result.organization + "\n"

        # newly created projects
        created_project = result.createdProjects
        if not created_project:
            output += "No new projects found \n"
        else:
            created_projects_num = len(created_project)
            output += str(created_projects_num) + " newly created projects: "
            for project in created_project:
                output += project + " "

        # updated projects
        updated_projects = result.updatedProjects
        if not updated_projects:
            output += "\nNo projects were updated \n"
        else:
            updated_projects_num = len(updated_projects)
            output += str(updated_projects_num) + " existing projects were updated: "
            for project in updated_projects:
                output += project + " "
            output += "\nrequest_token: " + result.orgToken
        print(output)
    else:
        print("There was a problem with the update result")
        logging.debug("The update result is empty")


def offline_request(project_info, token, product_name, product_version):
    """ Offline request """

    projects = [project_info]
    off_request = UpdateInventoryRequest(token, product_name, product_version, projects);

    if not os.path.exists(os.path.dirname(UPDATE_REQUEST_FILE)):
        try:
            os.makedirs(os.path.dirname(UPDATE_REQUEST_FILE))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(UPDATE_REQUEST_FILE, "w") as f:
        result = jsonpickle.encode(off_request, unpicklable=False)
        f.write(result)


def run_setup(file_name):
    """ Creates a list of package dependencies as a requirement string from the setup.py file"""
    req = open_required(file_name)
    # Todo: add functionality to run setuptools and wss_plugin logic on existing setup.py


def open_setup(file_name):
    """ Creates a list of package dependencies as a requirement string from the setup.py file"""

    import setuptools
    import mock
    req = []
    try:
        with mock.patch.object(setuptools, file_name) as mock_setup:
            import setup
        args, kwargs = mock_setup.call_args
        req = kwargs.get('install_requires', [])
        return req
    except Exception as err:
        print("No setup file", err.message)
        return req


def open_required_pip(file_name):
    install_requirements = parse_requirements(file_name, session='hack')
    records = [str(ir.req) for ir in install_requirements]
    #return open_required(file_name)
    return records

# todo deprecated.to be deleted in the next version
def open_required(file_name):
    """ Creates a list of package dependencies as a requirement string from the requirements.txt file"""

    req = []
    try:
        # Read the file and add each line in it as a dependency requirement string
        with open(file_name) as f:
            dependencies = f.read().splitlines()
        for dependency in dependencies:
            # discard requirements commands
            if dependency.startswith(DASH):
                if dependency.startswith(REQUIREMENTS):
                    next_file = dependency.split(SPACE)[1]
                    requirements = open_required(next_file)
                    for r in requirements:
                        req.append(r)
                continue
            else:
                req.append(dependency)
        return req
    except Exception as err:
        print("No requirements file", err.message)
        return req
