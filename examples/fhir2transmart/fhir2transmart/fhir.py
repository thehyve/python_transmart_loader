from datetime import date, datetime
from typing import Optional, Iterable

"""
FHIR resource classes, capturing a subset of the FHIR specification.
A more complete collection of Python classes is available at
  https://github.com/smart-on-fhir/client-py
"""

PatientIdentifier = str

EncounterIdentifier = str

Code = str


class Coding:
    """
    FHIR coding concept data type
    http://hl7.org/fhir/datatypes.html#Coding
    """
    def __init__(self, system: str, code: Code, display: Optional[str]):
        self.system = system
        self.code = code
        self.display = display


class CodeableConcept:
    """
    FHIR codeable concept data type
    http://hl7.org/fhir/datatypes.html#CodeableConcept
    """
    def __init__(self, coding: Iterable[Coding], text: str):
        self.coding = coding
        self.text = text


class Period:
    """
    FHIR period data type
    http://hl7.org/fhir/datatypes.html#Period
    """
    def __init__(self, start: date, end: date):
        self.start = start
        self.end = end


class PatientResource:
    """
    FHIR patient resource
    http://hl7.org/fhir/patient.html

    :param identifier a unique patient identifier
    :param gender see http://hl7.org/fhir/valueset-administrative-gender.html
    :param birth_date
    :param deceased
    :param deceased_date
    """
    def __init__(self,
                 identifier: PatientIdentifier,
                 gender: Code,
                 birth_date: Optional[date],
                 deceased: Optional[bool],
                 deceased_date: Optional[date]):
        self.identifier = identifier
        self.gender = gender
        self.birth_date = birth_date
        self.deceased = deceased
        self.deceased_date = deceased_date


class Encounter:
    """
    FHIR encounter resource
    http://hl7.org/fhir/encounter.html
    """
    def __init__(self,
                 identifier: EncounterIdentifier,
                 subject: PatientIdentifier,
                 period: Period,
                 status: str,
                 encounter_class: Coding,
                 hospitalization: str):
        self.identifier = identifier
        self.subject = subject
        self.period = period
        self.status = status
        self.encounter_class = encounter_class
        self.hospitalization = hospitalization


class Condition:
    """
    FHIR condition resource
    http://hl7.org/fhir/condition.html
    """
    def __init__(self,
                 subject: PatientIdentifier,
                 category: Optional[CodeableConcept],
                 code: CodeableConcept,
                 body_site: Optional[CodeableConcept],
                 encounter: Optional[EncounterIdentifier],
                 onset_date_time: Optional[datetime],
                 abatement_date_time: Optional[datetime],
                 recorded_date: Optional[date]):
        self.subject = subject
        self.category = category
        self.code = code
        self.body_site = body_site
        self.encounter = encounter
        self.onset_date_time = onset_date_time
        self.abatement_date_time = abatement_date_time
        self.recorded_date = recorded_date


class Collection:
    """
    FHIR data collection
    """
    def __init__(self,
                 patients: Iterable[PatientResource],
                 encounters: Iterable[Encounter],
                 conditions: Iterable[Condition]):
        self.patients = patients
        self.encounters = encounters
        self.conditions = conditions
