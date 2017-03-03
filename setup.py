#!/usr/bin/env python

import sys

from setuptools import setup, find_packages

if not sys.version_info[0] == 3:
    print('only python3 supported!')
    sys.exit(1)

setup(
    name='mecoSHARK',
    version='1.0.0',
    author='Fabian Trautsch',
    author_email='trautsch@cs.uni-goettingen.de',
    description='Calculates metrics and clones on revision level.',
    install_requires=['mongoengine', 'pymongo', 'pycoshark>=1.0.2', 'mock'],
    dependency_links=['git+https://github.com/smartshark/pycoSHARK.git@1.0.2#egg=pycoshark-1.0.2'],
    url='https://github.com/smartshark/mecoSHARK',
    download_url='https://github.com/smartshark/mecoSHARK/zipball/master',
    packages=find_packages(),
    test_suite = 'tests',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache2.0 License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
