###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

[Unreleased]
************

[1.4.0]
************

Changed
-------

* Removed Python 3.6 (unsupported)
* Added Python 3.9 and 3.10
* Updated the pydantic requirement to include versions up to 1.9.


[1.3.6]
************

Changed
-------

* Updated the pydantic requirement to include the 1.5 version.


[1.3.5]
************

Changed
-------

* Updated the pydantic requirement to include the 1.0 version.


[1.3.4]
************

Changed
-------

* Fix writing of tree nodes if parent node already exists


[1.3.3]
************

Changed
-------

* Fixed study node serialisation


[1.3.2]
************

Changed
-------

* Documentation updated


[1.3.1]
************

Changed
-------

* Fix tree node metadata type


[1.3.0]
************

Changed
-------

* Fix writing of study metadata


[1.2.1]
************

Changed
-------

* Fix writing of tree node tags


[1.2.0]
************

Added
-----

* Support for loading study metadata and tree node tags


[1.1.0]
************

Added
-----

* Support for loading relations and relation types


[1.0.0]
************

Added
-----

* Support for loading modifiers and modifier dimensions

Changed
-------

* Handling of visits and the encounter mapping is updated for compatibility
  with version 17.1-HYVE-6.0 of https://github.com/thehyve/transmart-core.


[0.1.3]
************

Added
-----

* Initial TranSMART loader package
