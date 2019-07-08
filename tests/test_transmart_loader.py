#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the transmart_loader module.
"""
from datetime import date
from os import path
from typing import List

import pytest

from transmart_loader.copy_writer import TransmartCopyWriter
from transmart_loader.transmart import DataCollection, Concept, Study, \
    TrialVisit, Visit, TreeNode, Patient, Observation, ValueType, StudyNode,\
    ConceptNode, CategoricalValue


def test_something():
    assert True


def test_with_error():
    with pytest.raises(ValueError):
        # Do something that raises a ValueError
        raise ValueError


@pytest.fixture
def empty_collection() -> DataCollection:
    concepts: List[Concept] = []
    studies: List[Study] = []
    trial_visits: List[TrialVisit] = []
    patients: List[Patient] = []
    visits: List[Visit] = []
    ontology: List[TreeNode] = []
    observations: List[Observation] = []
    collection = DataCollection(concepts, studies, trial_visits, visits,
                                ontology, patients, observations)
    return collection


@pytest.fixture
def simple_collection() -> DataCollection:
    concepts: List[Concept] = [
        Concept('dummy_code', 'Dummy variable', '\\dummy\\path',
                ValueType.Categorical)]
    studies: List[Study] = [Study('test', 'Test study')]
    trial_visits: List[TrialVisit] = [
        TrialVisit(studies[0], 'Week 1', 'Week', 1)]
    patients: List[Patient] = [Patient('SUBJ0', 'male', [])]
    visits: List[Visit] = [
        Visit(patients[0], 'visit1', None, None, None, None, None, None, [])]
    top_node = StudyNode(studies[0])
    top_node.add_child(ConceptNode(concepts[0]))
    ontology: List[TreeNode] = [top_node]
    observations: List[Observation] = [
        Observation(patients[0], concepts[0], visits[0], trial_visits[0],
                    date(2019, 3, 28), None, CategoricalValue('value'))]
    collection = DataCollection(concepts, studies, trial_visits, visits,
                                ontology, patients, observations)
    return collection


def test_load_empty_collection(tmp_path, empty_collection):
    target_path = tmp_path.as_posix()
    writer = TransmartCopyWriter(target_path)
    writer.write_collection(empty_collection)
    assert path.exists(target_path + '/i2b2metadata/i2b2_secure.tsv')
    assert path.exists(target_path + '/i2b2demodata/concept_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/patient_mapping.tsv')
    assert path.exists(target_path + '/i2b2demodata/patient_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/encounter_mapping.tsv')
    assert path.exists(target_path + '/i2b2demodata/visit_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/study.tsv')
    assert path.exists(target_path + '/i2b2metadata/dimension_description.tsv')
    assert path.exists(
        target_path + '/i2b2metadata/study_dimension_descriptions.tsv')
    assert path.exists(target_path + '/i2b2demodata/trial_visit_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/observation_fact.tsv')


def test_load_simple_collection(tmp_path, simple_collection):
    target_path = tmp_path.as_posix()
    writer = TransmartCopyWriter(target_path)
    writer.write_collection(simple_collection)
    assert path.exists(target_path + '/i2b2metadata/i2b2_secure.tsv')
    assert path.exists(target_path + '/i2b2demodata/concept_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/patient_mapping.tsv')
    assert path.exists(target_path + '/i2b2demodata/patient_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/encounter_mapping.tsv')
    assert path.exists(target_path + '/i2b2demodata/visit_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/study.tsv')
    assert path.exists(target_path + '/i2b2metadata/dimension_description.tsv')
    assert path.exists(
        target_path + '/i2b2metadata/study_dimension_descriptions.tsv')
    assert path.exists(target_path + '/i2b2demodata/trial_visit_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/observation_fact.tsv')
