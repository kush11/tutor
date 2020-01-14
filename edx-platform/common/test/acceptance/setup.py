#!/usr/bin/env python

"""
Install bok-choy page objects for acceptance and end-to-end tests.
"""

import os

from setuptools import setup

VERSION = '0.0.1'
DESCRIPTION = "Bok-choy page objects for edx-platform"

# Pip 1.5 will try to install this package from outside
# the directory containing setup.py, so we need to use an absolute path.
ACCEPTANCE_PACKAGE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)))

setup(
    name='edxapp-acceptance',
    version=VERSION,
    author='edX',
    url='http://github.com/edx/edx-platform',
    description=DESCRIPTION,
    license='AGPL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance'
    ],
    package_dir={'edxapp_acceptance': ACCEPTANCE_PACKAGE_DIR},
    packages=['edxapp_acceptance',
              'edxapp_acceptance.pages',
              'edxapp_acceptance.pages.lms',
              'edxapp_acceptance.pages.studio',
              'edxapp_acceptance.pages.common',
              'edxapp_acceptance.tests']
)
