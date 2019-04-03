from typing import List, Optional, Dict, Iterable

from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.encounter import Encounter
import fhirclient.models.patient as fhir_patient
from fhirclient.models.fhirreference import FHIRReference
from transmart_loader.loader_exception import LoaderException

from .fhir import Collection, Condition

from transmart_loader.transmart import DataCollection, Patient, Concept, \
    Observation, TreeNode, Visit, TrialVisit, Study, ValueType, DateValue, \
    CategoricalValue, ConceptNode

gender_concept = Concept(
    'gender', 'Gender', 'gender', ValueType.Categorical)

birth_date_concept = Concept(
    'birth_date', 'Birth date', 'birth_date', ValueType.Date)

patient_concepts = ['gender', 'birth_date']

study = Study('FHIR', 'FHIR')

trial_visit = TrialVisit(study, '', 0, '')


def map_concept(codeable_concept: CodeableConcept) -> Concept:
    """
    Maps a codeable concept to a TranSMART concept.
    The system and code are both used for the concept code and the path.
    The value type is always Categorical.

    :param codeable_concept: the codeable concept
    :return: a TranSMART Concept entity
    """
    concept_code = '{}/{}'.format(
        codeable_concept.coding[0].system,
        codeable_concept.coding[0].code)
    return Concept(
        concept_code,
        codeable_concept.text,
        concept_code,
        ValueType.Categorical
    )


def get_reference(ref_obj: FHIRReference) -> Optional[str]:
    """
    Returns a reference string from a FHIR Reference if it exists.

    :param ref_obj: the FHIR Reference object
    :return: the reference string or None
    """
    if ref_obj is None:
        return None
    reference: str = ref_obj.reference
    if reference is None:
        return None
    if not reference.startswith('urn:uuid:'):
        raise LoaderException('Invalid reference: {}'.format(reference))
    return reference[len('urn:uuid:'):]


class Mapper:
    """
    FHIR to TranSMART mapping
    """
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.studies: List[Study] = [study]
        self.trial_visits: List[TrialVisit] = [trial_visit]
        self.visits: Dict[str, Visit] = {}
        self.patient_nodes: List[TreeNode] = []
        self.ontology_nodes: List[TreeNode] = []
        self.patients: Dict[str, Patient] = {}
        self.observations: List[Observation] = []

    def add_ontology_node(self, concept: Concept) -> None:
        if concept.concept_code in patient_concepts:
            self.patient_nodes.append(ConceptNode(concept))
        else:
            self.ontology_nodes.append(ConceptNode(concept))

    def add_concept(self, concept: Concept) -> None:
        if concept.concept_code not in self.concepts:
            self.concepts[concept.concept_code] = concept
            self.add_ontology_node(concept)

    def add_observation(self, observation: Observation) -> None:
        self.add_concept(observation.concept)
        self.observations.append(observation)

    def map_patient(self, patient: fhir_patient.Patient) -> None:
        """ Maps a FHIR Patient Resource to a Patient entity in TranSMART.
        The gender and birthDate are mapped to a Date Observation entity.
        The Patient and Observations are added to the collections of
        Patients and Observations returned by the mapper.

        :param patient: a FHIR Patient Resource
        """
        subject = Patient(patient.id, patient.gender, [])
        self.patients[patient.id] = subject
        gender_observation = Observation(
            subject,
            gender_concept,
            None,
            trial_visit,
            None,
            None,
            CategoricalValue(patient.gender))
        self.add_observation(gender_observation)
        birth_date_observation = Observation(
            subject,
            birth_date_concept,
            None,
            trial_visit,
            None,
            None,
            DateValue(patient.birthDate.date))
        self.add_observation(birth_date_observation)

    def map_encounter(self, encounter: Encounter) -> None:
        """ Maps an FHIR Encounter Resource to a Visit entity in TranSMART.
        The reference to the subject is resolved to the corresponding TranSMART Patient.
        The Visit is added to the collection of Visits returned by the mapper.

        :param encounter: a FHIR Encounter Resource
        """
        subject = self.patients[get_reference(encounter.subject)]
        visit = Visit(
            subject,
            encounter.id,
            encounter.status,
            encounter.period.start.date if encounter.period else None,
            encounter.period.end.date if encounter.period else None,
            encounter.class_fhir.code if encounter.class_fhir else None,
            encounter.hospitalization,
            None
        )
        self.visits[encounter.id] = visit

    def map_condition(self, condition: Condition) -> None:
        """ Maps a FHIR Condition Resource to a categorical Observation entity
        in TranSMART.
        The reference to the subject is resolved to the corresponding TranSMART Patient.
        The reference to the encounter is resolved to the corresponding TranSMART Visit.
        The Observation is added to the collection of Observations returned by the mapper.

        :param condition: a FHIR Condition Resource
        """
        subject = self.patients[get_reference(condition.subject)]
        visit_ref = get_reference(condition.encounter)
        if visit_ref is None:
            visit_ref = get_reference(condition.context)
        visit = self.visits[visit_ref] if visit_ref else None
        concept = map_concept(condition.code)
        observation = Observation(
            subject,
            concept,
            visit,
            trial_visit,
            None,
            None,
            CategoricalValue(concept.name)
        )
        self.add_observation(observation)

    def map_collection(self, collection: Collection) -> None:
        """ Maps a collection of FHIR Resources, in the following order:
         Patients, Encounters, Conditions.

        :param collection: a collection of FHIR Resources.
        """
        for patient in collection.patients:
            self.map_patient(patient)
        for encounter in collection.encounters:
            self.map_encounter(encounter)
        for condition in collection.conditions:
            self.map_condition(condition)

    def get_ontology(self) -> Iterable[TreeNode]:
        """ Returns a forest of directed acyclic graphs of ontology nodes.

        :return: the root nodes
        """
        patient_root = TreeNode('Patient')
        for node in self.patient_nodes:
            patient_root.add_child(node)
        ontology_root = TreeNode('Ontology')
        for node in self.ontology_nodes:
            ontology_root.add_child(node)
        return [patient_root, ontology_root]

    @staticmethod
    def map(collection: Optional[Collection]) -> Optional[DataCollection]:
        """ Maps a collection of FHIR Resources to a collection of TranSMART
         entities.

        :param collection: the collection of FHIR Resources
        :return: a TranSMART data collection
        """
        if collection is None:
            return None
        mapper = Mapper()
        mapper.map_collection(collection)
        return DataCollection(
            mapper.concepts.values(),
            mapper.studies,
            mapper.trial_visits,
            mapper.visits.values(),
            mapper.get_ontology(),
            mapper.patients.values(),
            mapper.observations)
