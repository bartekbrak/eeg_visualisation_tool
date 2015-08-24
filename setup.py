from setuptools import setup, find_packages

setup(
    name='evt',
    version='2015.08.24.1',
    packages=find_packages(include=('evt*',)),
    include_package_data=True,
    install_requires=[
        'bokeh==0.9.2',
        # FIXME: not needed anymore, just numpy
        'ipython[notebook]',
        'openpyxl==2.2.5',
        'Flask==0.10.1',
        'WTForms==2.0.2',
        'ffprobe==0.5',
        'joblib==0.8.4',
    ],
    entry_points={
        'console_scripts': [
            'evt_standalone = evt.server:standalone',
            'evt_server = evt.server:main',
        ]
    }
)
