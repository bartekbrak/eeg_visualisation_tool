from setuptools import setup, find_packages

setup(
    name='evt',
    version='2015.08.10.4',
    packages=find_packages(include=('evt*',)),
    include_package_data=True,
    install_requires=[
        'bokeh==0.9.1',
        'ipython[notebook]',
        'openpyxl==2.2.5',
        'Flask==0.10.1',
        'WTForms==2.0.2',
    ],
    entry_points={
        'console_scripts': [
            'evt_standalone = evt.standalone:standalone',
            'evt_server = evt.server:main',
        ]
    }
)
