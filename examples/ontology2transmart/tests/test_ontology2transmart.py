#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the ontology2transmart module.
"""
from typing import List

import pytest

from ontology2transmart.ontology_writer import OntologyWriter


@pytest.fixture
def mock_chapters() -> List[List[str]]:
    return [
        ['01', 'First chapter'],
        ['02', 'Second chapter']
    ]


@pytest.fixture
def mock_groups() -> List[List[str]]:
    return [
        ['A00', 'A21', '01', 'First group'],
        ['A02', 'A27', '01', 'Second group'],
        ['B00', 'B10', '02', 'Third group']
    ]


def create_mode_code_row(level: int,
                         node_type: str,
                         code_type: str,
                         chapter: str,
                         group: str,
                         code: str,
                         name: str) -> List[str]:
    return [
        level,
        node_type,
        code_type,
        chapter,
        group,
        code,
        None,
        None,
        name,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None
    ]


@pytest.fixture
def mock_codes() -> List[List[str]]:
    return [
        create_mode_code_row(3, 'N', 'X', '01', 'A00', 'A00.-', 'First subgroup'),
        create_mode_code_row(4, 'T', 'X', '01', 'A00', 'A00.1', 'First concept'),
        create_mode_code_row(3, 'N', 'X', '01', 'A00', 'A01.-', 'Second subgroup'),
        create_mode_code_row(4, 'T', 'X', '01', 'A00', 'A01.5', 'Second concept'),
        create_mode_code_row(3, 'N', 'X', '01', 'A02', 'A02.-', 'Third subgroup'),
        create_mode_code_row(4, 'T', 'X', '01', 'A02', 'A02.1', 'Third concept'),
        create_mode_code_row(4, 'T', 'X', '01', 'A02', 'A02.2', 'Fourth concept'),
        create_mode_code_row(3, 'N', 'X', '02', 'B00', 'B05.-', 'Fourth subgroup'),
        create_mode_code_row(4, 'T', 'X', '02', 'B00', 'B05.3', 'Fifth concept')
    ]


def test_write_ontology(mock_chapters, mock_groups, mock_codes):
    writer = OntologyWriter('http://mock.system')
    for chapter in mock_chapters:
        writer.process_chapter_row(chapter)
    for group in mock_groups:
        writer.process_group_row(group)
    for code in mock_codes:
        writer.process_code_row(code)
    assert len(writer.mapper.concepts) == 5
    assert len(writer.mapper.chapter_nodes) == 2
