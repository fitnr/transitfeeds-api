#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of transitfeeds-api.
# https://github.com/fitnr/transitfeeds-api

# Licensed under the GPLv3 license
# Copyright (c) 2017, Neil Freeman <contact@fakeisthenewreal.org>
from setuptools import setup

try:
    readme = open('README.rst').read()
except IOError:
    readme = open('README.md').read()

with open('transitfeeds/__init__.py') as i:
    version = next(r for r in i.readlines() if '__version__' in r).split('=')[1].strip('"\' \n')

setup(
    name='transitfeeds-api',
    version=version,
    description='Python wrapper for transitfeeds.com',
    long_description='''Python wrapper for the transitfeeds.com API''',
    keywords='gtfs transit api',
    author='Neil Freeman',
    author_email='contact@fakeisthenewreal.org',
    url='https://github.com/fitnr/transitfeeds-api',
    license='GPLv3',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],
    packages=['transitfeeds'],
    include_package_data=False,
    install_requires=[
        'requests[security]>=2.13.0',
    ],
    entry_points={
        'console_scripts': [
            'transitfeeds=transitfeeds.cli:main',
        ],
    },
    test_suite='tests',
    zip_safe=True,
)
