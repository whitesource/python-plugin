import sys
import shutil
import tempfile
import hashlib
import logging
from distutils.sysconfig import get_python_lib

import pkg_resources as pk_res
from setuptools import Command
from setuptools.package_index import PackageIndex
from agent.api.model import PolicyCheckResourceNode

from agent.api.model.AgentProjectInfo import AgentProjectInfo
from agent.api.model.Coordinates import Coordinates
from agent.api.model.DependencyInfo import DependencyInfo
from agent.api.dispatch.UpdateInventoryRequest import UpdateInventoryRequest
from agent.api.dispatch.CheckPoliciesRequest import CheckPoliciesRequest
from agent.client.WssServiceClient import WssServiceClient


class SetupToolsCommand(Command):
    """setuptools Command"""
    description = "Setuptools WSS plugin"

    user_options = [
        ('pathConfig=', 'p', 'Configuration file path'),
        ('debug=', 'd', 'Show debugging output'),
    ]

    def initialize_options(self):
        self.debug = None
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
        if self.debug == 'y':
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

        # load and import config file
        try:
            sys.path.append(self.pathConfig)
            self.configDict = __import__('config_file').config_info
            logging.info('Loading config_file was successful')
        except Exception as err:
            sys.exit("Can't import the config file." + err.message)

        self.projectCoordinates = create_project_coordinates(self.distribution)
        self.userEnvironment = pk_res.Environment(get_python_lib(), platform=None, python=None)
        distribution_specification = self.distribution.get_name() + "==" + self.distribution.get_version()
        distribution_requirement = pk_res.Requirement.parse(distribution_specification)

        # resolve all dependencies
        try:
            self.distDepend = pk_res.working_set.resolve([distribution_requirement], env=self.userEnvironment)
            self.distDepend.pop(0)
            logging.info("Finished resolving dependencies")
        except Exception as err:
            print "distribution was not found on this system, and is required by this application", err.message

    def run(self):
        self.validate_config_file()
        self.scan_modules()
        self.create_service()
        project = self.create_project_obj()

        # send check policies request
        self.check_policies(project, self.configDict['org_token'], self.configDict['product_name'],
                            self.configDict['product_version'])
        # send update request
        self.update_inventory(project, self.configDict['org_token'], self.configDict['product_name'],
                              self.configDict['product_version'])

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
                    # create a distribution instance from requirement instance
                    current_requirement = dist.as_requirement()
                    current_distribution = self.pkgIndex.fetch_distribution(
                        current_requirement, self.tmpdir, force_scan=True, source=True, develop_ok=True)

                    # create dep. root
                    if current_distribution is not None:
                        self.dependencyList.append(create_dependency_record(current_distribution))

                except Exception as err:
                    print "Error in fetching distribution: " + dist
            logging.info("Finished calculation for all dependencies")
        else:
            logging.info("No dependencies were found")

        shutil.rmtree(self.tmpdir)

    def create_service(self):
        """ Creates a WssServiceClient instance with the destination url"""
        if ('url_destination' in self.configDict) and (self.configDict['url_destination'] != ''):
            self.service = WssServiceClient(self.configDict['url_destination'])
        else:
            self.service = WssServiceClient("https://saas.whitesourcesoftware.com/agent")

        logging.debug("The destination url is set to: " + self.service.to_string())

    def create_project_obj(self):
        """ create the actual project """

        project_token = self.configDict['project_token']
        if project_token == '':
            project_token = None
        return AgentProjectInfo(self.projectCoordinates, self.dependencyList, project_token)

    def check_policies(self, project_info, token, product_name, product_version):
        """ Sends the update request to the agent according to the request type """
        if self.configDict['check_policies']:
            logging.debug("Checking policies")
            projects = [project_info]
            request = CheckPoliciesRequest(token, product_name, product_version, projects)
            result = self.service.check_policies(request)
            try:
                self.handle_policies_result(result)
            except Exception as err:
                sys.exit("Some dependencies do not conform with open source policies")

    def handle_policies_result(self, result):
        """ Checks if any policies rejected if so stops """
        logging.debug("Creating policies report")
        if result.has_rejections():
            print_check_policies(result)
            logging.info("Some dependencies do not conform with open source policies")
            raise
        else:
            logging.debug("All dependencies conform with open source policies")

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
    dist_artifact = distribution.location.split('\\')[-1]
    dist_version = distribution.version
    dist_sha1 = calc_hash(distribution.location)
    dependency = DependencyInfo(group_id=dist_group, artifact_id=dist_artifact, version_id=dist_version, sha1=dist_sha1)
    return dependency


def create_project_coordinates(distribution):
    """ Creates a 'Coordinates' instance for the user package"""
    dist_name = distribution.get_name()
    dist_version = distribution.get_version()
    coordinates = Coordinates(group_id=None, artifact_id=dist_name, version_id=dist_version)
    return coordinates


def print_check_policies(result):
    """ Prints the result of the check policies result"""
    output = "Rejected Libraries:\n"
    if result.newProjects:
        output += print_project_policies_rejection(result.newProjects)
    if result.existingProjects:
        output += print_project_policies_rejection(result.existingProjects)

    print output


def print_project_policies_rejection(projects):
    """ Prints the the policy and corresponding rejected resources from projects"""
    output = ''

    # project iterator
    for project, resource_node in projects.iteritems():
        rejected_node = PolicyCheckResourceNode.find_rejected_node(resource_node)
        #rejected node iterator
        for node in rejected_node:
            # name
            output += "\t* " + node.resource.displayName

            # licenses
            licenses = node.resource.licenses
            if licenses:
                license_output = " ("
                for lice in licenses:
                    license_output += lice + ", "
                output += license_output[:-2] + ")"

            # policy
            output += " - Rejected by Policy " + '"' + node.policy.displayName + '"\n'

    return output


def print_update_result(result):
    """ Prints the result of the update result"""
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

    #updated projects
    updated_projects = result.updatedProjects
    if not updated_projects:
        output += "\nNo projects were updated \n"
    else:
        updated_projects_num = len(updated_projects)
        output += str(updated_projects_num) + " existing projects were updated: "
        for project in updated_projects:
            output += project + " "

    print output


def open_required(file_name):
    """ Creates a list of package dependencies as a requirement string from the file"""
    req = []
    try:
        # Read the file and add each line in it as a dependency requirement string
        with open(file_name) as f:
            dependencies = f.read().splitlines()
        for dependency in dependencies:
            req.append(dependency)
        return req
    except Exception as err:
        print "No requirements file", err.message
        return req