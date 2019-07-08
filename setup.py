#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup

if sys.version_info < (3, 6):
    sys.exit(
        'Python < 3.6 is not supported. You are using Python {}.{}.'.format(
            sys.version_info[0], sys.version_info[1])
    )

here = os.path.abspath(os.path.dirname(__file__))

# To update the package version number, edit transmart_loader/__version__.py
version = {}
with open(os.path.join(here, 'transmart_loader', '__version__.py')) as f:
    exec(f.read(), version)

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('requirements.txt', 'r') as f:
    required_packages = f.read().splitlines()

setup(
    name='transmart_loader',
    version=version['__version__'],
    description="Python library for loading data to TranSMART using transmart-copy",
    long_description=readme + '\n\n',
    author="Gijs Kant",
    author_email='gijs@thehyve.nl',
    url='https://github.com/thehyve/python_transmart_loader',
    packages=[
        'transmart_loader',
    ],
    package_dir={'transmart_loader':
                 'transmart_loader'},
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    keywords='transmart_loader',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    python_requires='>=3.6.0',
    install_requires=required_packages,
    setup_requires=[
        # dependency for `python setup.py test`
        'pytest-runner',
        # dependencies for `python setup.py build_sphinx`
        'sphinx',
        'sphinx_rtd_theme',
        'recommonmark',
        # dependency for `python setup.py bdist_wheel`
        'wheel'
    ],
    tests_require=[
        'pycodestyle',
        'pytest',
        'pytest-cov',
        'python-dateutil'
    ],
    extras_require={
        'dev':  ['prospector[with_pyroma]', 'yapf', 'isort'],
    }
)
