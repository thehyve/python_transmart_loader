from abc import abstractmethod
from datetime import date
from enum import Enum
from typing import Any, Sequence, List, Iterable, Optional


class ValueType(Enum):
    """
    Type of an observed value
    """
    Numeric = 1
    Categorical = 2
    Text = 3
    Date = 4


class PatientMapping:
    """
    Patient identifiers
    """
    def __init__(self, source: str, identifier: str):
        self.source = source
        self.identifier = identifier


class Patient:
    """
    Patient properties
    """
    def __init__(self,
                 identifier: str,
                 sex: str,
                 mappings: Sequence[PatientMapping]):
        self.identifier = identifier
        self.sex = sex
        self.mappings = mappings


class Concept:
    """
    Concepts to classify observations
    """
    def __init__(self,
                 concept_code: str,
                 name: str,
                 concept_path: str,
                 value_type: ValueType):
        self.concept_code = concept_code
        self.name = name
        self.concept_path = concept_path
        self.value_type = value_type


class Visit:
    """
    Patient visit
    """
    def __init__(self, patient: Patient,
                 identifier: str,
                 active_status: Optional[str],
                 start_date: Optional[date],
                 end_date: Optional[date],
                 inout: Optional[str],
                 location: Optional[str],
                 length_of_stay: Optional[int]):
        self.patient = patient
        self.identifier = identifier  # TODO: remove identifier field
        self.active_status = active_status
        self.start_date = start_date
        self.end_date = end_date
        self.inout = inout
        self.location = location
        self.length_of_stay = length_of_stay


class Study:
    """
    Study
    """
    def __init__(self, study_id: str, name: str):
        self.study_id = study_id
        self.name = name


class Dimension:
    """
    Dimension metadata
    """
    def __init__(self,
                 name: str,
                 modifier_code: Optional[str],
                 value_type: Optional[ValueType]):
        self.name = name
        self.modifier_code = modifier_code
        self.value_type = value_type


class TrialVisit:
    """
    Trial visit
    """
    def __init__(self,
                 study: Study,
                 rel_time_unit: Optional[str],
                 rel_time: Optional[int],
                 rel_time_label: str):
        self.study = study
        self.rel_time_unit = rel_time_unit
        self.rel_time = rel_time
        self.rel_time_label = rel_time_label


class ObservationMetadata:
    """
    Metadata about an observation
    """


class Value:
    """
    An observed value
    """
    @property
    @abstractmethod
    def value_type(self) -> ValueType:
        pass

    @property
    @abstractmethod
    def value(self) -> Any:
        pass


class NumericalValue(Value):
    """
    A numerical value
    """
    def __init__(self, value: float):
        self._value = value

    def value_type(self):
        return ValueType.Numeric

    def value(self):
        return self._value


class DateValue(Value):
    """
    A date value
    """
    def __init__(self, value: date):
        self._value = value

    def value_type(self):
        return ValueType.Date

    def value(self):
        return self._value


class CategoricalValue(Value):
    """
    A categorical value
    """
    def __init__(self, value: str):
        self._value = value

    def value_type(self):
        return ValueType.Categorical

    def value(self):
        return self._value


class TextValue(Value):
    """
    A text value
    """
    def __init__(self, value: str):
        self._value = value

    def value_type(self):
        return ValueType.Text

    def value(self):
        return self._value


class Observation:
    """
    Data about an observed event or an attribute of a patient
    """
    def __init__(self,
                 patient: Patient,
                 concept: Concept,
                 visit: Optional[Visit],
                 trial_visit: TrialVisit,
                 start_date: Optional[date],
                 end_date: Optional[date],
                 value: Value):
        self.patient = patient
        self.concept = concept
        self.visit = visit
        self.trial_visit = trial_visit
        self.start_date = start_date
        self.end_date = end_date
        self.value = value


class TreeNode:
    """
    Ontology node
    """
    def __init__(self, name: str):
        self.parent: Optional['TreeNode'] = None
        self.name = name
        self.children: List[TreeNode] = []

    def add_child(self, child: 'TreeNode'):
        self.children.append(child)


class StudyNode(TreeNode):
    """
    Study node
    """
    def __init__(self, study: Study):
        TreeNode.__init__(self, study.name)
        self.study = study


class ConceptNode(TreeNode):
    """
    Concept node
    """
    def __init__(self, concept: Concept):
        TreeNode.__init__(self, concept.name)
        self.concept = concept


class DataCollection:
    """
    A data collection that can be loaded into TranSMART
    """
    def __init__(self,
                 concepts: Iterable[Concept],
                 studies: Iterable[Study],
                 trial_visits: Iterable[TrialVisit],
                 visits: Iterable[Visit],
                 ontology: Iterable[TreeNode],
                 patients: Iterable[Patient],
                 observations: Iterable[Observation]):
        self.concepts = concepts
        self.studies = studies
        self.trial_visits = trial_visits
        self.visits = visits
        self.ontology = ontology
        self.patients = patients
        self.observations = observations
