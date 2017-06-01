from setuptools import setup

setup(
    name='wss_plugin',
    version='1.1.2',
    description='Wss python pluging for creating/updating wss organization inventory',
    author='Yossi Weinberg',
    author_email='yossi.weinberg@whitesourcesoftware.com',
    install_requires=["requests == 2.13.0", "enum34 == 1.1.6", "jsonpickle == 0.9.4"],
    packages=['plugin', 'agent', 'agent.client', 'agent.api', 'agent.api.dispatch', 'agent.api.model'],
    include_package_data=True,
    license="Apache 2.0"
)
