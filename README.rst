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

.. _TranSMART: https://github.com/thehyve/transmart-core
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

Define a TranSMART data collection, using the classes in `transmart_loader/transmart.py`_, e.g.,

.. _`transmart_loader/transmart.py`: https://github.com/thehyve/python_transmart_loader/blob/master/transmart_loader/transmart.py

.. code-block:: python

  # Create the dimension elements
  age_concept = Concept('test:age', 'Age', '\\Test\\age', ValueType.Numeric)
  concepts = [age_concept]
  studies = [Study('test', 'Test study')]
  trial_visits = [TrialVisit(studies[0], 'Week 1', 'Week', 1)]
  patients = [Patient('SUBJ0', 'male', [])]
  visits = [Visit(patients[0], 'visit1', None, None, None, None, None, None, [])]
  # Create the observations
  observations = [
      Observation(patients[0], age_concept, visits[0], trial_visits[0],
                  date(2019, 3, 28), None, NumericalValue(28))]

Create a hierarchical ontology for the concepts, e.g., to create the following structure:

::
  
  └ Ontology
    └ Age


.. code-block:: python

  # Create an ontology with one top node and a concept node
  top_node = TreeNode('Ontology')
  top_node.add_child(ConceptNode(concepts[0]))
  ontology = [top_node]

Write the data collection to a format that can be loaded using ``transmart-copy``:

.. code-block:: python

  collection = DataCollection(concepts, [], [], studies,
                              trial_visits, visits, ontology, patients, observations)
  
  # Write collection to a temporary directory
  # The generated files can be loaded into TranSMART with transmart-copy.
  output_dir = mkdtemp()
  copy_writer = TransmartCopyWriter(output_dir)
  copy_writer.write_collection(collection)


Check `examples/data_collection.py`_ for a complete example.

.. _`examples/data_collection.py`: https://github.com/thehyve/python_transmart_loader/blob/master/examples/data_collection.py

Usage examples can be found in these projects: 

- `fhir2transmart <https://github.com/thehyve/python_fhir2transmart>`_: a tool that translates core `HL7 FHIR`_ resources to the TranSMART data model.  
- `claml2transmart <https://github.com/thehyve/python_claml2transmart>`_: a tool that translates ontologies in ClaML_ format (e.g., ICD-10, available from DIMDI_)
  to TranSMART ontologies.
- `csr2transmart <https://github.com/thehyve/python_csr2transmart>`_: a custom data transformation
  and loading pipeline for a Dutch center for pediatric oncology.
- `transmart-hyper-dicer <https://github.com/thehyve/transmart-hyper-dicer>`_: a tool that reads a selection of data from a TranSMART instance using its REST API
  and loads it into another TranSMART instance.

.. _`HL7 FHIR`: http://hl7.org/fhir/
.. _DIMDI: https://www.dimdi.de
.. _ClaML: https://www.iso.org/standard/69318.html


Documentation
*************

Full documentation of the package is available at `Read the Docs`_.

.. _Read the Docs: https://transmart-loader.readthedocs.io


Development
*************

For a quick reference on software development, we refer to `the software guide checklist <https://guide.esciencecenter.nl/best_practices/checklist.html>`_.

Python versions
---------------

This packages is tested with Python versions 3.6 and 3.7.

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

This project was funded by the German Ministry of Education and Research (BMBF) as part of the project
DIFUTURE - Data Integration for Future Medicine within the German Medical Informatics Initiative (grant no. 01ZZ1804D).

This package was created with `Cookiecutter <https://github.com/audreyr/cookiecutter>`_ and the `NLeSC/python-template <https://github.com/NLeSC/python-template>`_.
