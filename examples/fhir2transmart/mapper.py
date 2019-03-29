from typing import List, Optional, Dict

from fhir import Collection, PatientResource, Condition, Encounter, CodeableConcept

from transmart_loader.transmart import DataCollection, Patient, Concept, \
    Observation, TreeNode, Visit, TrialVisit, Study, ValueType, DateValue, CategoricalValue

birth_date_concept = Concept(
    'birth_date', 'Birth date', 'birth_date', ValueType.Date)

study = Study('FHIR', 'FHIR')

trial_visit = TrialVisit(study, '', 0, '')


def map_concept(codeable_concept: CodeableConcept) -> Concept:
    concept_code = codeable_concept.coding[0].system + '/' + codeable_concept.coding[0].code
    return Concept(
        concept_code,
        codeable_concept.text,
        concept_code,
        ValueType.Categorical
    )


class Mapper:
    """
    FHIR to TranSMART mapping

    FIXME: extend with creating ontology nodes
    """
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.studies: List[Study] = [study]
        self.trial_visits: List[TrialVisit] = [trial_visit]
        self.visits: List[Visit] = []
        self.ontology: List[TreeNode] = []
        self.patients: Dict[str, Patient] = {}
        self.observations: List[Observation] = []

    def add_concept(self, concept: Concept) -> None:
        if concept.concept_code not in self.concepts:
            self.concepts[concept.concept_code] = concept

    def add_observation(self, observation: Observation) -> None:
        self.add_concept(observation.concept)
        self.observations.append(observation)

    def map_patient(self, patient: PatientResource) -> None:
        subject = Patient(patient.identifier, patient.gender, [])
        self.patients[patient.identifier] = subject
        birth_date_observation = Observation(
            subject,
            birth_date_concept,
            None,
            trial_visit,
            None,
            None,
            DateValue(patient.birth_date))
        self.add_observation(birth_date_observation)

    def map_encounter(self, encounter: Encounter) -> None:
        subject = self.patients[encounter.subject]
        visit = Visit(
            subject,
            encounter.identifier,
            encounter.status,
            encounter.period.start if encounter.period else None,
            encounter.period.end if encounter.period else None,
            encounter.encounter_class,
            encounter.hospitalization,
            None
        )
        self.visits.append(visit)

    def map_condition(self, condition: Condition) -> None:
        subject = self.patients[condition.subject]
        concept = map_concept(condition.code)
        observation = Observation(
            subject,
            concept,
            None,
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
        return DataCollection(
            mapper.concepts.values(),
            mapper.studies,
            mapper.trial_visits,
            mapper.visits,
            mapper.ontology,
            mapper.patients.values(),
            mapper.observations)
