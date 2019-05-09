#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the fhir2transmart module.
"""

import pytest

from fhir2transmart.fhir_reader import FhirReader
from fhir2transmart.mapper import Mapper

from transmart_loader.transmart import DataCollection


@pytest.fixture
def empty_fhir_bundle() -> dict:
    return {
        'resourceType': 'Bundle',
        'type': 'collection',
        'entry': [

        ]
    }


@pytest.fixture
def simple_fhir_bundle() -> dict:
    return {
        'resourceType': 'Bundle',
        'type': 'collection',
        'entry': [
            {
                'resource': {
                    'resourceType': 'Patient',
                    'id': 'SUBJ0',
                    'birthDate': '2000-01-01',
                    'gender': 'female'
                }
            },
            {
                'resource': {
                    'resourceType': 'Encounter',
                    'id': 'VISIT0',
                    'subject': {
                        'reference': 'urn:uuid:SUBJ0'
                    },
                    'status': 'finished',
                    'period': {
                        'start': '2010-12-10T09:30',
                        'end': '2010-12-10T17:00'
                    }
                }
            },
            {
                'resource': {
                    'resourceType': 'Condition',
                    'subject': {
                        'reference': 'urn:uuid:SUBJ0'
                    },
                    'code': {
                        'text': 'Decease X',
                        'coding': [{
                            'system': 'ICD-10',
                            'code': 'Code-X'
                        }]
                    },
                    'bodySite': [{
                        'text': 'Head',
                        'coding': [{
                            'system': 'SNOMEDCTBodyStructures',
                            'code': 'Example body site'
                        }]
                    }],
                    'encounter': {
                        'reference': 'urn:uuid:VISIT0'
                    },
                    'onsetDateTime': '2010-10-01T13:15'
                }
            },
            {
                'resource': {
                    'resourceType': 'Patient',
                    'id': 'SUBJ1',
                    'birthDate': '2002-12-10',
                    'gender': 'male'
                }
            },
            {
                'resource': {
                    'resourceType': 'Encounter',
                    'id': 'VISIT1',
                    'subject': {
                        'reference': 'urn:uuid:SUBJ1'
                    },
                    'status': 'finished',
                    'class': {
                        'code': 'in'
                    }
                }
            },
            {
                'resource': {
                    'resourceType': 'Condition',
                    'subject': {
                        'reference': 'urn:uuid:SUBJ1'
                    },
                    'code': {
                        'text': 'Decease Y',
                        'coding': [{
                            'system': 'ICD-10',
                            'code': 'Code-Y'
                        }]
                    },
                    'encounter': {
                        'reference': 'urn:uuid:VISIT1'
                    },
                    'onsetDateTime': '2010-04-01T13:15',
                    'abatementDateTime': '2010-08-01T13:15'
                }
            },
        ]
    }


def test_read_empty_bundle(empty_fhir_bundle):
    collection = FhirReader.read(empty_fhir_bundle)
    result = Mapper.map(collection)
    assert len(result.studies) == 1
    assert len(result.patients) == 0


def test_read_simple_bundle(simple_fhir_bundle):
    collection = FhirReader.read(simple_fhir_bundle)
    result: DataCollection = Mapper.map(collection)
    assert len(result.studies) == 1
    assert len(result.patients) == 2
    assert len(result.visits) == 2
    assert len(result.observations) == 6
