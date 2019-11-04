#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the transmart_loader module.
"""
import csv
from datetime import date, datetime
from os import path
from typing import List

import pytest

from transmart_loader.copy_writer import TransmartCopyWriter
from transmart_loader.transmart import DataCollection, Concept, Study, \
    TrialVisit, Visit, TreeNode, Patient, Observation, ValueType, StudyNode, \
    ConceptNode, CategoricalValue, Modifier, ObservationMetadata, \
    TextValue, DateValue, Dimension, DimensionType, RelationType, Relation, \
    TreeNodeMetadata, StudyMetadata


@pytest.fixture
def empty_collection() -> DataCollection:
    concepts: List[Concept] = []
    modifiers: List[Modifier] = []
    dimensions: List[Dimension] = []
    studies: List[Study] = []
    trial_visits: List[TrialVisit] = []
    patients: List[Patient] = []
    visits: List[Visit] = []
    ontology: List[TreeNode] = []
    observations: List[Observation] = []
    collection = DataCollection(concepts, modifiers, dimensions, studies,
                                trial_visits, visits, ontology, patients,
                                observations)
    return collection


@pytest.fixture
def simple_collection() -> DataCollection:
    concepts: List[Concept] = [
        Concept('dummy_code', 'Dummy variable', '\\dummy\\path',
                ValueType.Categorical),
        Concept('diagnosis_date', 'Diagnosis date', '\\diagnosis_date',
                ValueType.Date),
        Concept('extra_c1', 'Extra c1', '\\c1', ValueType.Categorical),
        Concept('extra_c2', 'Extra c2', '\\c1', ValueType.Categorical)]
    modifiers: List[Modifier] = [
        Modifier('missing_value', 'Missing value', '\\missing_value',
                 ValueType.Text),
        Modifier('sample_id', 'Sample ID', '\\sample_id',
                 ValueType.Numeric)]
    dimensions: List[Dimension] = [
        Dimension('sample', modifiers[1], DimensionType.Subject, 1)
    ]
    study_metadata = StudyMetadata(**{'conceptCodeToVariableMetadata': {
        'test_concept': {
            'name': 'variable_1',
            'type': 'DATETIME'
        }
    }})
    studies: List[Study] = [Study('test', 'Test study', study_metadata)]
    trial_visits: List[TrialVisit] = [
        TrialVisit(studies[0], 'Week 1', 'Week', 1)]
    patients: List[Patient] = [Patient('SUBJ0', 'male', [])]
    visits: List[Visit] = [
        Visit(patients[0], 'visit1', None, None, None, None, None, None, [])]
    top_node = StudyNode(studies[0])
    top_node.metadata = TreeNodeMetadata(
        {'Upload date': '2019-07-01'})
    top_node.add_child(ConceptNode(concepts[0]))
    top_node.add_child(ConceptNode(concepts[1]))

    node2 = TreeNode('Extra node')
    node2.add_child((ConceptNode(concepts[2])))
    node3 = TreeNode('Extra node')
    node3.add_child(ConceptNode(concepts[3]))

    ontology: List[TreeNode] = [top_node, node2, node3]
    observations: List[Observation] = [
        Observation(patients[0], concepts[0], visits[0], trial_visits[0],
                    date(2019, 3, 28), None, CategoricalValue('value')),
        Observation(patients[0], concepts[0], visits[0], trial_visits[0],
                    datetime(2019, 6, 26, 12, 34, 00),
                    datetime(2019, 6, 28, 16, 46, 13, 345),
                    CategoricalValue(None),
                    ObservationMetadata({
                        modifiers[0]: TextValue('Invalid')
                    })),
        Observation(patients[0], concepts[1], visits[0], trial_visits[0],
                    datetime(2019, 6, 26, 13, 50, 10), None,
                    DateValue(datetime(2018, 4, 30, 17, 10, 00)))
    ]
    collection = DataCollection(concepts, modifiers, dimensions, studies,
                                trial_visits, visits, ontology, patients,
                                observations)
    return collection


@pytest.fixture
def collection_with_relations() -> DataCollection:
    concepts: List[Concept] = [
        Concept('dummy_code', 'Dummy variable', '\\dummy\\path',
                ValueType.Categorical)]
    studies: List[Study] = [Study('test', 'Test study')]
    trial_visits: List[TrialVisit] = [
        TrialVisit(studies[0], 'Week 1', 'Week', 1)]
    patients: List[Patient] = [
        Patient('SUBJ0', 'male', []),
        Patient('SUBJ1', 'female', []),
        Patient('SUBJ2', 'female', [])
    ]
    visits: List[Visit] = [
        Visit(patients[0], 'visit1', None, None, None, None, None, None, [])]
    top_node = StudyNode(studies[0])
    top_node.add_child(ConceptNode(concepts[0]))
    ontology: List[TreeNode] = [top_node]
    relation_types = [RelationType('parent', None, None, None),
                      RelationType('sibling', 'Sibling of', True, True)]
    relations = [
        Relation(patients[0], relation_types[0], patients[1], None, None),
        Relation(patients[0], relation_types[0], patients[2], None, None),
        Relation(patients[1], relation_types[1], patients[2], True, True)]
    collection = DataCollection(concepts, [], [], studies,
                                trial_visits, visits, ontology, patients,
                                [], relation_types, relations)
    return collection


def get_column_values(file_path: str, column_name: str) -> List[str]:
    rows = []
    with open(file_path) as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            rows.append(row[column_name])
    return rows


def test_load_empty_collection(tmp_path, empty_collection):
    target_path = tmp_path.as_posix()
    writer = TransmartCopyWriter(target_path)
    writer.write_collection(empty_collection)
    assert path.exists(target_path + '/i2b2metadata/i2b2_secure.tsv')
    assert path.exists(target_path + '/i2b2metadata/i2b2_tags.tsv')
    assert path.exists(target_path + '/i2b2demodata/concept_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/modifier_dimension.tsv')
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
    del writer

    assert path.exists(target_path + '/i2b2metadata/i2b2_secure.tsv')
    tree_node_paths = get_column_values(target_path + '/i2b2metadata/i2b2_secure.tsv', 'c_fullname')
    assert len(tree_node_paths) == 6
    assert all(elem in tree_node_paths for elem in [
        '\\Test study\\', '\\Test study\\Dummy variable\\', '\\Test study\\Diagnosis date\\',
        '\\Extra node\\', '\\Extra node\\Extra c1\\', '\\Extra node\\Extra c2\\'])
    assert path.exists(target_path + '/i2b2metadata/i2b2_tags.tsv')
    assert path.exists(target_path + '/i2b2demodata/concept_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/modifier_dimension.tsv')
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


def test_load_collection_with_relations(tmp_path, collection_with_relations):
    target_path = tmp_path.as_posix()
    writer = TransmartCopyWriter(target_path)
    writer.write_collection(collection_with_relations)
    assert path.exists(target_path + '/i2b2metadata/i2b2_secure.tsv')
    assert path.exists(target_path + '/i2b2metadata/i2b2_tags.tsv')
    assert path.exists(target_path + '/i2b2demodata/concept_dimension.tsv')
    assert path.exists(target_path + '/i2b2demodata/modifier_dimension.tsv')
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
    assert path.exists(target_path + '/i2b2demodata/relation_types.tsv')
    assert path.exists(target_path + '/i2b2demodata/relations.tsv')
