#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the transmart_loader module.
"""
from os import path
from typing import List

import pytest

from transmart_loader.copy_writer import TransmartCopyWriter
from transmart_loader.transmart import DataCollection, Concept, Study,\
    TrialVisit, Visit, TreeNode, Patient, Observation


def test_something():
    assert True


def test_with_error():
    with pytest.raises(ValueError):
        # Do something that raises a ValueError
        raise(ValueError)


# Fixture example
@pytest.fixture
def empty_collection() -> DataCollection:
    concepts: List[Concept] = []
    studies: List[Study] = []
    trial_visits: List[TrialVisit] = []
    visits: List[Visit] = []
    ontology: List[TreeNode] = []
    patients: List[Patient] = []
    observations: List[Observation] = []
    collection = DataCollection(concepts, studies, trial_visits, visits,
                                ontology, patients, observations)
    return collection


def test_transmart_loader(tmp_path, empty_collection):
    target_path = tmp_path.as_posix()
    writer = TransmartCopyWriter(target_path)
    writer.write_collection(empty_collection)
    assert path.exists(target_path + '/i2b2metadata/i2b2_secure.tsv')
    assert path.exists(target_path + '/i2b2demodata/concept_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/patient_dimension.tsv')
    # assert path.exists(target_path + '/i2b2demodata/visit_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/study.tsv')
    assert path.exists(target_path + '/i2b2demodata/trial_visit_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/observation_fact.tsv')
