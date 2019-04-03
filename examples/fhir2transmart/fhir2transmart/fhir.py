from typing import Iterable
import fhirclient.models.condition as condition
import fhirclient.models.encounter as encounter
import fhirclient.models.fhirreference as fhirreference
import fhirclient.models.patient as patient

"""
FHIR resource classes, capturing a subset of the FHIR specification.

This package contains extensions of the collection of Python classes
 available at https://github.com/smart-on-fhir/client-py
"""


class Condition(condition.Condition):
    """ Detailed information about conditions, problems or diagnoses.

    Extends the Condition definition from
        https://github.com/smart-on-fhir/client-py with:
    - encounter
    """

    def __init__(self, jsondict=None, strict=True):
        """ Initialize all valid properties.

        :raises: FHIRValidationError on validation errors, unless strict is False
        :param dict jsondict: A JSON dictionary to use for initialization
        :param bool strict: If True (the default), invalid variables will raise a TypeError
        """

        self.encounter = None
        """ The Encounter during which this Condition was created
        or to which the creation of this record is tightly associated.
        Type `Reference` (represented as `dict` in JSON). """

        super(Condition, self).__init__(jsondict=jsondict, strict=strict)

    def elementProperties(self):
        js = super(Condition, self).elementProperties()
        js.extend([
            ("encounter", "encounter", fhirreference.FHIRReference, False, None, False),
        ])
        return js


class Collection:
    """
    FHIR data collection, containing Patient, Encounter and Condition resources
    """
    def __init__(self,
                 patients: Iterable[patient.Patient],
                 encounters: Iterable[encounter.Encounter],
                 conditions: Iterable[Condition]):
        self.patients = patients
        self.encounters = encounters
        self.conditions = conditions
