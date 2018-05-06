from setuptools import setup

setup(
    name='wss_plugin',
    version='18.4.2-SNAPSHOT',
    description='Wss python pluging for creating/updating wss organization inventory',
    author='Yossi Weinberg',
    author_email='yossi.weinberg@whitesourcesoftware.com',
    install_requires=["requests == 2.14.2", "enum34 == 1.1.6", "jsonpickle == 0.9.4", "mock == 2.0.0", "pip"],
    packages=['plugin', 'agent', 'agent.client', 'agent.api', 'agent.api.dispatch', 'agent.api.model'],
    include_package_data=True,
    license="Apache 2.0"
)
