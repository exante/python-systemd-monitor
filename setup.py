#!/usr/bin/env python

import os
from distutils.util import convert_path
from setuptools import setup, find_packages

location = os.path.abspath(os.path.dirname(__file__))
with open('README.md') as readme:
    description = readme.read()
metadata = dict()
with open(convert_path('src/systemd_monitor/version.py')) as metadata_file:
    exec(metadata_file.read(), metadata)


setup(
    name='systemd_monitor',
    version=metadata['__version__'],

    description='Library functions to monitor state of systemd spawned units',
    long_description=description,

    url='https://github.com/exante/systemd_monitor',
    author='EXANTE',
    author_email='',

    license='MIT',

    keywords='systemd',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    zip_safe=False,

    install_requires=[
        'dbus'
    ]
)
