#!/usr/bin/env python

import sys

from setuptools import setup, find_packages

if not sys.version_info[0] == 3:
    print('only python3 supported!')
    sys.exit(1)

setup(
    name='mecoSHARK',
    version='0.10',
    description='Calculates metrics and clones on revision level.',
    install_requires=['mongoengine', 'pymongo'],
    author='Fabian Trautsch',
    author_email='ftrautsch@googlemail.com',
    url='https://github.com/smartshark/mecoSHARK',
    test_suite='tests',
    packages=find_packages(),
    zip_safe=False,
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
