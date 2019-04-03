from typing import List, Sequence

from fhirclient.models.fhirreference import FHIRReference

from .fhir import Condition, Collection

import fhirclient.models.encounter as encounter
import fhirclient.models.patient as patient

from transmart_loader.console import Console
from transmart_loader.loader_exception import LoaderException


def read_patient(data: dict) -> patient.Patient:
    return patient.Patient(data, False)


def read_encounter(data: dict) -> encounter.Encounter:
    result = encounter.Encounter(data, False)
    if 'subject' in data:
        result.subject = FHIRReference(data['subject'], False)
    return result


def read_condition(data: dict) -> Condition:
    result = Condition(data, False)
    if 'subject' in data:
        result.subject = FHIRReference(data['subject'], False)
    if 'encounter' in data:
        result.encounter = FHIRReference(data['encounter'], False)
    return result


class FhirReader:
    """
    Reads FHIR resources from JSON
    """
    def __init__(self):
        self.patients: List[patient.Patient] = []
        self.encounters: List[encounter.Encounter] = []
        self.conditions: List[Condition] = []

    def read_resource(self, data: dict) -> None:
        resource_type = data['resourceType']
        if resource_type == 'Patient':
            self.patients.append(read_patient(data))
        elif resource_type == 'Encounter':
            self.encounters.append(read_encounter(data))
        elif resource_type == 'Condition':
            self.conditions.append(read_condition(data))
        else:
            Console.warning(
                'Unsupported resource type ignored: {}'.format(resource_type))

    def read_resources(self, entries: Sequence[dict], resource_type: str) -> None:
        for entry in entries:
            resource = entry['resource']
            if resource['resourceType'] == resource_type:
                self.read_resource(resource)

    def read_bundle(self, data: dict) -> Collection:
        entries = data['entry']
        self.read_resources(entries, 'Patient')
        self.read_resources(entries, 'Encounter')
        self.read_resources(entries, 'Condition')
        return Collection(
            self.patients,
            self.encounters,
            self.conditions
        )

    @staticmethod
    def read(data: dict) -> Collection:
        """
        Parse FHIR collection from JSON
        :param data: JSON data
        :return: FHIR collection
        """
        resource_type = data['resourceType']
        if resource_type != 'Bundle':
            raise LoaderException(
                'Expected resource type Bundle, got {}'.format(
                    resource_type
                ))
        return FhirReader().read_bundle(data)
