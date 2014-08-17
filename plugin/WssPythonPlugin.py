import sys
import shutil
import tempfile
import hashlib
from distutils.sysconfig import get_python_lib

import pkg_resources as pk_res
from setuptools import Command
from setuptools.package_index import PackageIndex

from agent.api.dispatch.RequestType import RequestType
from agent.api.dispatch.CheckPoliciesRequest import CheckPoliciesRequest
from agent.api.model.AgentProjectInfo import AgentProjectInfo
from agent.api.model.Coordinates import Coordinates
from agent.api.model.DependencyInfo import DependencyInfo
from agent.api.dispatch.UpdateInventoryRequest import UpdateInventoryRequest
from agent.client.WssServiceClient import WssServiceClient


class SetupToolsCommand(Command):
    """setuptools Command"""
    description = "Setuptools WSS plugin"

    user_options = [
        ('pathConfig=', 'p', 'Configuration file path'),
    ]

    def initialize_options(self):
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
        try:
            sys.path.append(self.pathConfig)
            self.config_dict = __import__('config_file').config_info
        except Exception as err:
            print "Can't import the config file. ", err
        self.project_coordinates = create_project_coordinates(self.distribution)
        self.user_environment = pk_res.Environment(get_python_lib(), platform=None, python=None)
        distribution_specification = self.distribution.get_name() + "==" + self.distribution.get_version()
        distribution_requirement = pk_res.Requirement.parse(distribution_specification)
        try:
            self.dist_depend = pk_res.working_set.resolve([distribution_requirement], env=self.user_environment)
            self.dist_depend.pop(0)
        except Exception as err:
            print "distribution was not found on this system, and is required by this application", err

    def run(self):
        if self.dist_depend is not None:
            for dist in self.dist_depend:
                try:
                    current_requirement = dist.as_requirement()
                    current_distribution = self.pkg_index.fetch_distribution(current_requirement, self.tmpdir,
                                                                             force_scan=True, source=True,
                                                                             develop_ok=True)
                    if current_distribution is not None:
                        self.dependency_list.append(create_dependency_record(current_distribution))
                except Exception as err:
                    print "Error in fetching", dist, "distribution: ", err
            project = create_agent_project_info(self.project_coordinates, self.dependency_list,
                                                self.config_dict['project_token'])
            send_request(self.config_dict['request_type'], project, self.config_dict['org_token'],
                         self.config_dict['product_name'], self.config_dict['product_version'],
                         self.config_dict['url_destination'])
        else:
            "No dependencies were found"
        shutil.rmtree(self.tmpdir)


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


def create_agent_project_info(coordinates, dependencies, parent_coordinates=None, project_token=None):
    """ Creates a 'AgentProjectInfo' instance formatted to send as part of the http request to the agent """
    agent_project_info = AgentProjectInfo(coordinates, dependencies=dependencies, parent_coordinates=parent_coordinates,
                                          project_token=project_token)
    return agent_project_info


def send_request(request_type, project_info, token, product_name, product_version,
                 service_url="http://localhost/agent"):
    """ Sends the http request to the agent according to the request type """
    try:
        validate_config_file(request_type, token)
    except Exception as err:
        print "Config file is not properly set.", err
    request_factory = WssServiceClient(service_url)
    projects = [project_info]
    request_result = None

    if request_type == RequestType.UPDATE.__str__().split('.')[-1]:
        action = UpdateInventoryRequest(token, product_name, product_version, projects)
        request_result = request_factory.update_inventory(action)
    elif request_type == RequestType.CHECK_POLICIES.__str__().split('.')[-1]:
        action = CheckPoliciesRequest(token, product_name, product_version, projects)
        request_result = request_factory.check_policies(action)
    return request_result


def open_required(file_name):
    """ Creates a list of package dependencies as a requirement string from the file"""
    req = []
    with open(file_name) as f:
        dependencies = f.read().splitlines()
    for dependency in dependencies:
        req.append(dependency)
    return req


def validate_config_file(request_type, token):
    if (request_type != 'UPDATE') and (request_type != 'CHECK_POLICIES'):
        raise Exception("Invalid request type")
    if token is None:
        raise Exception("Empty domain token")
