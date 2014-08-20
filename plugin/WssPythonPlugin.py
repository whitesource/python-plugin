import sys
import shutil
import tempfile
import hashlib
import logging
from distutils.sysconfig import get_python_lib

import pkg_resources as pk_res
from setuptools import Command
from setuptools.package_index import PackageIndex

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
        self.config_dict = None
        self.pathConfig = None
        self.token = None
        self.user_environment = None
        self.dist_depend = None
        self.pkg_index = PackageIndex()
        self.dependency_list = []
        self.project_coordinates = None
        self.tmpdir = tempfile.mkdtemp(prefix="wss_python_plugin-")

    def finalize_options(self):
        if self.debug == 'y':
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

        # load and import config file
        try:
            sys.path.append(self.pathConfig)
            self.config_dict = __import__('config_file').config_info
            logging.info('Loading config_file was successful')
        except Exception as err:
            sys.exit("Can't import the config file." + err.message)

        self.project_coordinates = create_project_coordinates(self.distribution)
        self.user_environment = pk_res.Environment(get_python_lib(), platform=None, python=None)
        distribution_specification = self.distribution.get_name() + "==" + self.distribution.get_version()
        distribution_requirement = pk_res.Requirement.parse(distribution_specification)

        # resolve all dependencies
        try:
            self.dist_depend = pk_res.working_set.resolve([distribution_requirement], env=self.user_environment)
            self.dist_depend.pop(0)
            logging.info("Finished resolving dependencies")
        except Exception as err:
            print "distribution was not found on this system, and is required by this application", err.message

    def run(self):
        self.validate_config_file()
        self.scan_modules()
        self.create_service()

        # create the actual project
        project_token = self.config_dict['project_token']
        if project_token == '':
            project_token = None
        project = AgentProjectInfo(self.project_coordinates, self.dependency_list, project_token)

        # TODO send check policies request and handle result:
        # 1. create html
        # 2. If violation: exit
        # else - send update request

        # send update request
        self.update_inventory(project, self.config_dict['org_token'], self.config_dict['product_name'],
                              self.config_dict['product_version'])

    def validate_config_file(self):
        """ Validate content of config file params """
        # org token
        if 'org_token' in self.config_dict:
            if self.config_dict['org_token'] == '':
                sys.exit("Organization token is empty")
        else:
            sys.exit("No organization token option exists")

        logging.info("Validation of config file was successful")
        # Todo: check existence of other keys in dict

    def scan_modules(self):
        """ Downloads all the dependencies calculates their sha1 and creates a list of dependencies info"""

        if self.dist_depend is not None:
            for dist in self.dist_depend:
                try:
                    # create a distribution instance from requirement instance
                    current_requirement = dist.as_requirement()
                    current_distribution = self.pkg_index.fetch_distribution(
                        current_requirement, self.tmpdir, force_scan=True, source=True, develop_ok=True)

                    # create dep. root
                    if current_distribution is not None:
                        self.dependency_list.append(create_dependency_record(current_distribution))

                except Exception as err:
                    print "Error in fetching distribution: " + dist
            logging.info("Finished calculation for all dependencies")
        else:
            logging.info("No dependencies were found")

        shutil.rmtree(self.tmpdir)

    def create_service(self):
        """ Creates a WssServiceClient instance with the destination url"""
        if ('url_destination' in self.config_dict) and (self.config_dict['url_destination'] != ''):
            self.service = WssServiceClient(self.config_dict['url_destination'])
        else:
            self.service = WssServiceClient("https://saas.whitesourcesoftware.com/agent")

        logging.debug("The destination url is set to: " + self.service.to_string())

    def update_inventory(self, project_info, token, product_name, product_version):
        """ Sends the update request to the agent according to the request type """
        logging.debug("Updating White Source")
        projects = [project_info]
        request = UpdateInventoryRequest(token, product_name, product_version, projects)
        result = self.service.update_inventory(request)
        print_update_result(result)

    def check_policies(self, project_info, token, product_name, product_version):
        """ Sends the update request to the agent according to the request type """
        logging.debug("Checking policies")
        projects = [project_info]
        request = UpdateInventoryRequest(token, product_name, product_version, projects)
        result = self.service.check_policies(request)
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


def print_update_result(result):
    """ Prints the result of the http request"""
    output = "White Source update results: \n"
    output += "White Source organization: " + result.organization + "\n"

    # newly created projects
    created_project = result.created_projects
    if not created_project:
        output += "No new projects found \n"
    else:
        created_projects_num = len(created_project)
        output += str(created_projects_num) + " Newly created projects: "
        for project in created_project:
            output += project + ", "

    #updated projects
    updated_projects = result.updated_projects
    if not updated_projects:
        output += "\nNo projects were updated \n"
    else:
        updated_projects_num = len(updated_projects)
        output += str(updated_projects_num) + " existing projects were updated: "
        for project in updated_projects:
            output += project + ", "

    print output


#def handle_policy_result(result):

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


