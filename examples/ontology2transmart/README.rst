################################################################################
Example ontology to TranSMART loader
################################################################################


Installation
------------

The package requires Python 3.6.

To install ``ontology2transmart``, do:

.. code-block:: console

  git clone https://github.com/thehyve/python_transmart_loader.git
  cd python_transmart_loader
  pip install .
  cd examples/ontology2transmart
  pip install .


Run tests (including coverage) with:

.. code-block:: console

  python setup.py test


Usage
-----

Read ontology from a collection of TSV files from `DIMDI`_ and write the output in transmart-copy
format to ``/path/to/output``. The output directory should be
empty of not existing (then it will be created).
E.g., the ICD-10-GM (German modification of ICD-10) is available at icd10gm2019syst-meta.zip_.

.. code-block:: console

  python -m ontology2transmart.ontology2transmart input/ /path/to/output

.. _DIMDI: https://www.dimdi.de
.. _icd10gm2019syst-meta.zip: https://www.dimdi.de/dynamic/.downloads/klassifikationen/icd-10-gm/version2019/icd10gm2019syst-meta.zip


License
-------

Copyright (c) 2019, The Hyve

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
