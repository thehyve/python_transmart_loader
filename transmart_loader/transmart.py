from abc import abstractmethod
from datetime import date
from enum import Enum
from typing import Any, Sequence, List, Iterable, Optional, Dict


class ValueType(Enum):
    """
    Type of an observed value
    """
    Numeric = 1
    Categorical = 2
    Text = 3
    Date = 4


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
    def __init__(self, value: Optional[float]):
        self._value = value

    @property
    def value_type(self):
        return ValueType.Numeric

    @property
    def value(self):
        return self._value


class DateValue(Value):
    """
    A date value
    """
    def __init__(self, value: Optional[date]):
        self._value = value

    @property
    def value_type(self):
        return ValueType.Date

    @property
    def value(self):
        return self._value


class CategoricalValue(Value):
    """
    A categorical value
    """
    def __init__(self, value: Optional[str]):
        self._value = value

    @property
    def value_type(self):
        return ValueType.Categorical

    @property
    def value(self):
        return self._value


class TextValue(Value):
    """
    A text value
    """
    def __init__(self, value: Optional[str]):
        self._value = value

    @property
    def value_type(self):
        return ValueType.Text

    @property
    def value(self):
        return self._value


class DimensionType(Enum):
    """
    Type of a dimension
    """
    Subject = 1
    Attribute = 2


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


class Modifier:
    """
    Metadata type
    """
    def __init__(self,
                 modifier_code: str,
                 name: str,
                 modifier_path: str,
                 value_type: ValueType):
        self.modifier_code = modifier_code
        self.name = name
        self.modifier_path = modifier_path
        self.value_type = value_type


class IdentifierMapping:
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
                 mappings: Sequence[IdentifierMapping]):
        self.identifier = identifier
        self.sex = sex
        self.mappings = mappings


class RelationType:
    """
    Relation type
    """
    def __init__(self,
                 label: str,
                 description: Optional[str],
                 symmetrical: Optional[bool],
                 biological: Optional[bool]
                 ):
        self.label = label
        self.description = description
        self.symmetrical = symmetrical
        self.biological = biological


class Relation:
    """
    Binary relation between patients
    """
    def __init__(self,
                 left: Patient,
                 relation_type: RelationType,
                 right: Patient,
                 biological: Optional[bool],
                 share_household: Optional[bool]):
        self.left = left
        self.relation_type = relation_type
        self.right = right
        self.biological = biological
        self.share_household = share_household


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
                 length_of_stay: Optional[int],
                 mappings: Sequence[IdentifierMapping]):
        self.patient = patient
        self.identifier = identifier
        self.active_status = active_status
        self.start_date = start_date
        self.end_date = end_date
        self.inout = inout
        self.location = location
        self.length_of_stay = length_of_stay
        self.mappings = mappings


class StudyMetadata:
    """
    Metadata about a study
    """
    def __init__(self, values: Dict[str, Value]):
        self.values = values


class Study:
    """
    Study
    """
    def __init__(self,
                 study_id: str,
                 name: str,
                 metadata: Optional[StudyMetadata] = None):
        self.study_id = study_id
        self.name = name
        self.metadata = metadata


class Dimension:
    """
    Dimension metadata
    """
    def __init__(self,
                 name: str,
                 modifier: Optional[Modifier] = None,
                 dimension_type: Optional[DimensionType] = None,
                 sort_index: Optional[int] = None):
        self.name = name
        self.modifier = modifier
        self.dimension_type = dimension_type
        self.sort_index = sort_index


class TrialVisit:
    """
    Trial visit
    """
    def __init__(self,
                 study: Study,
                 rel_time_label: str,
                 rel_time_unit: Optional[str] = None,
                 rel_time: Optional[int] = None):
        self.study = study
        self.rel_time_unit = rel_time_unit
        self.rel_time = rel_time
        self.rel_time_label = rel_time_label


class ObservationMetadata:
    """
    Metadata about an observation
    """
    def __init__(self, values: Dict[Modifier, Value]):
        self.values = values


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
                 value: Value,
                 metadata: Optional[ObservationMetadata] = None):
        self.patient = patient
        self.concept = concept
        self.visit = visit
        self.trial_visit = trial_visit
        self.start_date = start_date
        self.end_date = end_date
        self.value = value
        self.metadata = metadata


class TreeNodeMetadata:
    """
    Metadata tags
    """
    def __init__(self, values: Dict[str, Value]):
        self.values = values


class TreeNode:
    """
    Ontology node
    """
    def __init__(self, name: str, metadata: Optional[TreeNodeMetadata] = None):
        self.parent: Optional['TreeNode'] = None
        self.name = name
        self.metadata = metadata
        self.children: Sequence['TreeNode'] = []

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
                 modifiers: Iterable[Modifier],
                 dimensions: Iterable[Dimension],
                 studies: Iterable[Study],
                 trial_visits: Iterable[TrialVisit],
                 visits: Iterable[Visit],
                 ontology: Iterable[TreeNode],
                 patients: Iterable[Patient],
                 observations: Iterable[Observation],
                 relation_types: Iterable[RelationType] = [],
                 relations: Iterable[Relation] = []):
        self.concepts = concepts
        self.modifiers = modifiers
        self.dimensions = dimensions
        self.studies = studies
        self.trial_visits = trial_visits
        self.visits = visits
        self.ontology = ontology
        self.patients = patients
        self.observations = observations
        self.relation_types = relation_types
        self.relations = relations
