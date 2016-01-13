#!/usr/bin/env python
import os
from setuptools import setup, find_packages
import awesome_gallery

print os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-awesome-gallery',
    version=".".join(map(str, awesome_gallery.__version__)),
    author='Francisco Vaquero',
    author_email='akura11.tt@gmail.com',
    intall_requires=[
        'Django>=7.0',
        'boto',
        'dateutil',
        'python-mimeparse=>0.1.4',
        'django-tastypie',
    ],
    description='Simple and awesome gallery media system for Django',
    # data_files=
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development" 
    ]   
)
