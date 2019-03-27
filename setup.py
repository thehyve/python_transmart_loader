#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# To update the package version number, edit transmart_loader/__version__.py
version = {}
with open(os.path.join(here, 'transmart_loader', '__version__.py')) as f:
    exec(f.read(), version)

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='transmart_loader',
    version=version['__version__'],
    description="",
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
    license="GNU General Public License v3 or later",
    zip_safe=False,
    keywords='transmart_loader',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    install_requires=[],  # FIXME: add your package's dependencies to this list
    setup_requires=[
        # dependency for `python setup.py test`
        'pytest-runner',
        # dependencies for `python setup.py build_sphinx`
        'sphinx',
        'sphinx_rtd_theme',
        'recommonmark'
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pycodestyle',
    ],
    extras_require={
        'dev':  ['prospector[with_pyroma]', 'yapf', 'isort'],
    }
)
