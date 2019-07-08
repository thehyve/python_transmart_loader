TranSMART loader
================

|Build status| |codecov| |pypi| |status| |downloads| |license|

.. |Build status| image:: https://travis-ci.org/thehyve/python_transmart_loader.svg?branch=master
   :alt: Build status
   :target: https://travis-ci.org/thehyve/python_transmart_loader/branches
.. |codecov| image:: https://codecov.io/gh/thehyve/python_transmart_loader/branch/master/graph/badge.svg
   :alt: codecov
   :target: https://codecov.io/gh/thehyve/python_transmart_loader
.. |pypi| image:: https://img.shields.io/pypi/v/transmart_loader.svg
   :alt: PyPI
   :target: https://pypi.org/project/transmart_loader/
.. |status| image:: https://img.shields.io/pypi/status/transmart-loader.svg
   :alt: PyPI - Status
.. |downloads| image:: https://img.shields.io/pypi/dm/transmart-loader.svg
   :alt: PyPI - Downloads
.. |license| image:: https://img.shields.io/pypi/l/transmart_loader.svg
   :alt: MIT license
   :target: LICENSE

This package contains classes that represent the core domain objects stored in the TranSMART_ platform,
an open source data sharing and analytics platform for translational biomedical research.

It also provides a utility that writes such objects to tab-separated files that can be loaded into
a TranSMART database using the transmart-copy_ tool.

.. _TranSMART: https://github.com/thehyve/transmart_core
.. _transmart-copy: https://github.com/thehyve/transmart-core/tree/dev/transmart-copy

⚠️ Note: this is a development version.
Issues can be reported at https://github.com/thehyve/python_transmart_loader/issues.


Installation and usage
**********************

To install transmart_loader, do:

.. code-block:: console

  pip install transmart-loader

or from sources:

.. code-block:: console

  git clone https://github.com/thehyve/python_transmart_loader.git
  cd python_transmart_loader
  pip install .


Usage
------

Usage examples can be found in these projects: 

- `fhir2transmart <https://github.com/thehyve/python_fhir2transmart>`_: a tool that translates core `HL7 FHIR`_ resources to the TranSMART data model.  
- `ontology2transmart <https://github.com/thehyve/python_ontology2transmart>`_: a tool that translates ontologies available from DIMDI_
  to TranSMART ontologies.

.. _`HL7 FHIR`: http://hl7.org/fhir/
.. _DIMDI: https://www.dimdi.de


Documentation
*************

Full documentation of the package is available at `Read the Docs`_.

.. _Read the Docs: https://transmart-loader.readthedocs.io


Development
*************

For a quick reference on software development, we refer to `the software guide checklist <https://guide.esciencecenter.nl/best_practices/checklist.html>`_.

Python versions
---------------

This repository is set up with Python version 3.6

Add or remove Python versions based on project requirements. `The guide <https://guide.esciencecenter.nl/best_practices/language_guides/python.html>`_ contains more information about Python versions and writing Python 2 and 3 compatible code.

Package management and dependencies
-----------------------------------

This project uses `pip` for installing dependencies and package management.

* Dependencies should be added to `setup.py` in the `install_requires` list.

Testing and code coverage
-------------------------

* Tests are in the ``tests`` folder.
* The ``tests`` folder contains:

  - A test if files for `transmart-copy` are generated for fake data (file: ``test_transmart_loader``)
  - A test that checks whether your code conforms to the Python style guide (PEP 8) (file: ``test_lint.py``)

* The testing framework used is `PyTest <https://pytest.org>`_

  - `PyTest introduction <http://pythontesting.net/framework/pytest/pytest-introduction/>`_

* Tests can be run with ``python setup.py test``

Documentation
-------------

* Documentation should be put in the ``docs`` folder.

* To generate html documentation run ``python setup.py build_sphinx``

Coding style conventions and code quality
-----------------------------------------

* Check your code style with ``prospector``
* You may need run ``pip install .[dev]`` first, to install the required dependencies


License
*******

Copyright (c) 2019 The Hyve B.V.

The TranSMART loader is licensed under the MIT License. See the file `<LICENSE>`_.


Credits
*******

This package was created with `Cookiecutter <https://github.com/audreyr/cookiecutter>`_ and the `NLeSC/python-template <https://github.com/NLeSC/python-template>`_.
