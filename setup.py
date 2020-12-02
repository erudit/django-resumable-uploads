# coding: utf-8
__author__ = 'Consortium Érudit'

from setuptools import setup, find_packages

setup(
    name="django-resumable-uploads",
    version="1.0.11",
    description="""
django-resumable-uploads is a multi file upload app for django.
Uses plupload""",
    long_description=open('README.md').read(),
    author="Consortium Erudit",
    author_email="tech@erudit.org",
    url="",
    license="GPLv2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['django', 'humanfriendly', 'simplejson'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "License :: OSI Approved :: BSD License",
        'Topic :: Software Development :: Libraries :: Python Modules ',
        ],
    zip_safe=False,
)
