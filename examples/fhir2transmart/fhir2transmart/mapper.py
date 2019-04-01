from typing import List, Optional, Dict

import fhirclient.models.codeableconcept as codeableconcept
import fhirclient.models.encounter as encounter
import fhirclient.models.patient as patient
import fhirclient.models.fhirreference as fhirreference

from .fhir import Collection, Condition

from transmart_loader.transmart import DataCollection, Patient, Concept, \
    Observation, TreeNode, Visit, TrialVisit, Study, ValueType, DateValue, \
    CategoricalValue, ConceptNode

birth_date_concept = Concept(
    'birth_date', 'Birth date', 'birth_date', ValueType.Date)

patient_concepts = ['birth_date']

study = Study('FHIR', 'FHIR')

trial_visit = TrialVisit(study, '', 0, '')


def map_concept(codeable_concept: codeableconcept.CodeableConcept) -> Concept:
    concept_code = '{}/{}'.format(
        codeable_concept.coding[0].system,
        codeable_concept.coding[0].code)
    return Concept(
        concept_code,
        codeable_concept.text,
        concept_code,
        ValueType.Categorical
    )


def get_reference(ref_obj: fhirreference.FHIRReference) -> Optional[str]:
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

    def map_patient(self, patient: patient.Patient) -> None:
        subject = Patient(patient.id, patient.gender, [])
        self.patients[patient.id] = subject
        birth_date_observation = Observation(
            subject,
            birth_date_concept,
            None,
            trial_visit,
            None,
            None,
            DateValue(patient.birthDate.date))
        self.add_observation(birth_date_observation)

    def map_encounter(self, encounter: encounter.Encounter) -> None:
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
        for patient in collection.patients:
            self.map_patient(patient)
        for encounter in collection.encounters:
            self.map_encounter(encounter)
        for condition in collection.conditions:
            self.map_condition(condition)

    @staticmethod
    def map(collection: Optional[Collection]) -> Optional[DataCollection]:
        if collection is None:
            return None
        mapper = Mapper()
        mapper.map_collection(collection)
        patient_root = TreeNode('Patient')
        for node in mapper.patient_nodes:
            patient_root.add_child(node)
        ontology_root = TreeNode('Ontology')
        for node in mapper.ontology_nodes:
            ontology_root.add_child(node)
        ontology = [patient_root, ontology_root]
        return DataCollection(
            mapper.concepts.values(),
            mapper.studies,
            mapper.trial_visits,
            mapper.visits.values(),
            ontology,
            mapper.patients.values(),
            mapper.observations)
