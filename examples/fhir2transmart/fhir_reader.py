from datetime import date
from typing import List, Optional, Any, Sequence

from dateutil import parser
from fhir import PatientResource, Encounter, Condition, Coding, CodeableConcept,\
    Collection, Period

from transmart_loader.console import Console
from transmart_loader.loader_exception import LoaderException


def read_value(data: dict, key: str) -> Any:
    if not data or key not in data:
        Console.error('Object: {}'.format(data))
        raise LoaderException('Missing attribute {}'.format(key))
    return data[key]


def read_optional(data: dict, key: str) -> Optional[Any]:
    if key not in data:
        return None
    return data[key]


def read_reference(data: dict, key: str) -> Optional[str]:
    ref_obj = read_optional(data, key)
    if ref_obj is None:
        return None
    reference: str = read_optional(ref_obj, 'reference')
    if reference is None:
        return None
    if not reference.startswith('urn:uuid:'):
        raise LoaderException('Invalid reference: {}'.format(reference))
    return reference[len('urn:uuid:'):]


def read_date_time(data: dict, key: str) -> Optional[date]:
    if key not in data:
        return None
    return parser.parse(data[key])


def read_date(data: dict, key: str) -> Optional[date]:
    if key not in data:
        return None
    return parser.parse(data[key])


def read_coding(data: dict) -> Coding:
    return Coding(
        read_value(data, 'system'),
        read_value(data, 'code'),
        read_optional(data, 'display')
    )


def read_codeable_concept(
    data: dict) -> Sequence[CodeableConcept]:
    codings: List[Coding] = []
    for item in data['coding']:
        codings.append(read_coding(item))
    return CodeableConcept(
        codings,
        read_optional(data, 'text')
    )


def read_period(data: dict) -> Period:
    return Period(
        read_date_time(data, 'start'),
        read_date_time(data, 'end')
    )


def read_patient(data: dict) -> PatientResource:
    return PatientResource(
        read_value(data, 'id'),
        read_value(data, 'gender'),
        read_date(data, 'birthDate'),
        read_optional(data, 'deceased'),
        read_date(data, 'deceasedDate')
    )


def read_encounter(data: dict) -> Encounter:
    return Encounter(
        read_value(data, 'id'),
        read_reference(data, 'subject'),
        read_period(data['period']) if 'period' in data else None,
        read_optional(data, 'status'),
        read_optional(data, 'class'),
        read_optional(data, 'hospitalization')
    )


def read_condition(data: dict) -> Condition:
    return Condition(
        read_reference(data, 'subject'),
        read_codeable_concept(data['category']) if 'category' in data else [],
        read_codeable_concept(data['code']) if 'code' in data else None,
        read_codeable_concept(data['bodySite']) if 'bodySite' in data else [],
        read_optional(data, 'encounter'),
        read_date_time(data, 'onsetDateTime'),
        read_date_time(data, 'abatementDateTime'),
        read_date(data, 'recordedDate')
    )


class FhirReader:
    """
    Reads FHIR resources from JSON
    """
    def __init__(self):
        self.patients: List[PatientResource] = []
        self.encounters: List[Encounter] = []
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
        bundle_type = data['type']
        if bundle_type != 'collection':
            raise LoaderException(
                'Expected bundle type collection, got {}'.format(
                    bundle_type
                ))
        return FhirReader().read_bundle(data)
