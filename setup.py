#!/usr/bin/env python
from setuptools import setup, find_packages
import awesome_gallery

setup(
    name='django_awesome_gallery',
    version=".".join(map(str, awesome_gallery.__version__)),
    author='Francisco Vaquero',
    author_email='akura11.tt@gmail.com',
    intall_requires=[
        'Django>=1.0',
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
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development" 
    ]   
)
