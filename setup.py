from setuptools import setup, find_packages

setup(
    name='evt',
    version='2015.07.19.1',
    packages=find_packages(include=('evt*',)),
    entry_points={
        'console_scripts': [
            'evt_standalone = evt.standalone:standalone',
            'evt_server = evt.server:main',
        ]
    }
)
