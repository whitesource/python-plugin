from setuptools import setup

setup(
    name='WssPlugin',
    version='1.0',
    description='Wss python pluging for creating/updating wss organization inventory',
    author='Yossi Weinberg',
    author_email='yossi.weinberg@whitesourcesoftware.com',

    install_requires=["requests == 2.3.0"],
    packages=['agent', 'agent.dispatch', 'agent.model', 'plugin'],
    include_package_data=True,

)
