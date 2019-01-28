# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='cytobank-tools',
    version='0.1.0',
    description='Tools to handle Cytobank data',
    author='Anton Rau',
    author_email='anton.rau@uzh.ch',
    url='https://github.com/bodenmillerlab/cytobank-tools',
    packages=find_packages(include=['cytobank']),
    install_requires=[
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'cytobank=cytobank.cytobank:main',
        ],
    },
)
