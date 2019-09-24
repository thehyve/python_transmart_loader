from abc import abstractmethod
from datetime import date
from enum import Enum
from typing import Any, Sequence, Iterable, Optional, Dict, List

from pydantic import BaseModel


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
    Type of a dimension.

    Subject dimensions can be used for subselection,
    attribute dimensions only appear as additional dimension
    in the retrieved data.
    """
    Subject = 1
    Attribute = 2


class Concept:
    def __init__(self,
                 concept_code: str,
                 name: str,
                 concept_path: str,
                 value_type: ValueType):
        """
        Concepts to classify observations

        :param concept_code: A unique code for the concept.
                             it is recommended to prefix the code with a code for the coding system
                             of the ontology from which the concept originates.
        :param name: A descriptive label for the concept
        :param concept_path: A unique path for the concept. The concept_code can be reused for this.
        :param value_type: The value type for values associated with the concept.
        """
        self.concept_code = concept_code
        self.name = name
        self.concept_path = concept_path
        self.value_type = value_type


class Modifier:
    def __init__(self,
                 modifier_code: str,
                 name: str,
                 modifier_path: str,
                 value_type: ValueType):
        """
        Metadata type

        Defines a metadata type for observations. Examples are missing value codes,
        samples codes, method of data collection.

        :param modifier_code: a unique code for the metadata type.
        :param name: A descriptive label for the modifier.
        :param modifier_path: a unique path for the metadata type, the modifier_code can be reused for this.
        :param value_type: The value type for metadata values associated with the modifier.
        """
        self.modifier_code = modifier_code
        self.name = name
        self.modifier_path = modifier_path
        self.value_type = value_type


class IdentifierMapping:
    def __init__(self, source: str, identifier: str):
        """
        Patient or visit identifier

        The combination of source and identifier must be unique.

        :param source: the source system from which the identifier originates.
        :param identifier: the patient of visit identifier in the source system.
        """
        self.source = source
        self.identifier = identifier


class Patient:
    def __init__(self,
                 identifier: str,
                 sex: str,
                 mappings: Sequence[IdentifierMapping]):
        """
        Subject properties

        :param identifier: A unique identifier for the subject.
                           This identifier will appear in the identifier mapping
                           table with source 'SUBJ_ID'.
        :param sex: The sex of the subject. 'm' for male, 'f' for female. This field
                    is case-insensitive. Other values will be interpreted as unknown.
        :param mappings: additional identifiers for the subject. Warning: this
                         may be handled incorrectly by transmart-copy.
        """
        self.identifier = identifier
        self.sex = sex
        self.mappings = mappings


class RelationType:
    def __init__(self,
                 label: str,
                 description: Optional[str],
                 symmetrical: Optional[bool],
                 biological: Optional[bool]
                 ):
        """
        Relation type

        Represents a family or social relationship type.

        :param label: Short code for the relationship type.
        :param description: Descriptive label of the relationship type.
        :param symmetrical: Whether relations of this type are considered to be symmetrical,
                            e.g., True for siblings, False for parentOf.
        :param biological: Whether relations of this type are considered to be biological,
                            e.g., True for twins, False for teacherOf.
        """
        self.label = label
        self.description = description
        self.symmetrical = symmetrical
        self.biological = biological


class Relation:
    def __init__(self,
                 left: Patient,
                 relation_type: RelationType,
                 right: Patient,
                 biological: Optional[bool],
                 share_household: Optional[bool]):
        """
        Relation

        Represents binary family or social relations between subjects.

        :param left: one of the subjects
        :param relation_type: the relationship type
        :param right: the other subject
        :param biological: whether the relation is biological (e.g., to distinguish
                           biological siblings from non-biological siblings).
        :param share_household: whether the subjects are part of the same household.
        """
        self.left = left
        self.relation_type = relation_type
        self.right = right
        self.biological = biological
        self.share_household = share_household


class Visit:
    def __init__(self, patient: Patient,
                 identifier: str,
                 active_status: Optional[str],
                 start_date: Optional[date],
                 end_date: Optional[date],
                 inout: Optional[str],
                 location: Optional[str],
                 length_of_stay: Optional[int],
                 mappings: Sequence[IdentifierMapping]):
        """
        Patient visit

        Represents a clinical encounter.

        :param patient: the patient.
        :param identifier: A unique identifier for the visit.
                           This identifier will appear in the identifier mapping
                           table with source 'VISIT_ID'.
        :param active_status: Contains a code that represents the status of an event
                              along with the precision of the available dates.
        :param start_date: Start of the visit.
        :param end_date: End of the visit.
        :param inout: Code for the type of visit.
        :param location: Location code.
        :param length_of_stay: Duration of the visit.
        :param mappings: additional identifiers for the visit. Warning: this
                         may be handled incorrectly by transmart-copy.
        """
        self.patient = patient
        self.identifier = identifier
        self.active_status = active_status
        self.start_date = start_date
        self.end_date = end_date
        self.inout = inout
        self.location = location
        self.length_of_stay = length_of_stay
        self.mappings = mappings


class VariableDataType(str, Enum):
    """
    Variable data types in SPSS.
    """
    Numeric = 'NUMERIC'
    Date = 'DATE'
    DateTime = 'DATETIME'
    String = 'STRING'


class Measure(str, Enum):
    """
    Measure types in SPSS.
    """
    Nominal = 'NOMINAL'
    Ordinal = 'ORDINAL'
    Scale = 'SCALE'


class MissingValues(BaseModel):
    """
    Representating of missing values in SPSS.
    """
    lower: Optional[float]
    upper: Optional[float]
    values: Optional[List[Any]]
    value: Optional[Any]


class VariableMetadata(BaseModel):
    """
    Metadata of variables used for exporting to SPSS.
    """
    type: VariableDataType
    name: Optional[str]
    measure: Optional[Measure]
    description: Optional[str]
    width: Optional[int]
    decimals: Optional[int]
    columns: Optional[int]
    valueLabels: Optional[Dict[float, str]]
    missingValues: Optional[MissingValues]


class StudyMetadata(BaseModel):
    """
    Metadata about a study
    """
    conceptCodeToVariableMetadata: Optional[Dict[str, VariableMetadata]]
    """
    A map from concept code to variable metadata used to enable study specific
    exports of variables and values to SPSS.
    """


class Study:
    def __init__(self,
                 study_id: str,
                 name: str,
                 metadata: StudyMetadata = None):
        """
        Study

        :param study_id: A unique identifier for the study.
        :param name: A display label for the study.
        :param metadata: optional variable metadata, only used to enable exports to SPSS.
        """
        self.study_id = study_id
        self.name = name
        self.metadata = metadata


class Dimension:
    def __init__(self,
                 name: str,
                 modifier: Optional[Modifier] = None,
                 dimension_type: Optional[DimensionType] = None,
                 sort_index: Optional[int] = None):
        """
        Dimension metadata

        The TranSMART data model allows to specify additional dimensions,
        next to the default study, concept, patient, start time and visit dimensions.
        To add a dimension, create a Modifier, add a dimension linked to the modifier,
        and add metadata attributes to observations using the modifier as key.

        By default, all studies are linked to all dimensions specified, which means
        that all these dimensions will appear in the multidimensional data structure
        (hypercube) returned by the TranSMART API.

        :param name: The name of the dimension.
        :param modifier: The modifier used as key to add a dimension value to an observation
        :param dimension_type: the dimension type.
        :param sort_index: Used for subject dimensions to display the dimensions in desired order.
        """
        self.name = name
        self.modifier = modifier
        self.dimension_type = dimension_type
        self.sort_index = sort_index


class TrialVisit:
    def __init__(self,
                 study: Study,
                 rel_time_label: str,
                 rel_time_unit: Optional[str] = None,
                 rel_time: Optional[int] = None):
        """
        Trial visit

        Represents relative time in a clinical trial, e.g.,
        TrialVisit(study, 'Week 1', 'Week', 1) marks observations in the first week
        trial period.
        A trial visit always belongs to one study.
        If the data set does not represent a clinical trial, a placeholder
        trial visit can be created, e.g., TrialVisit(study, 'NA').

        :param study: the study the trial visit belongs to.
        :param rel_time_label: the display label for the trial visit.
        :param rel_time_unit: the unit of the relative time, e.g., 'hour' or 'week'.
        :param rel_time: the value of the relative time.
        """
        self.study = study
        self.rel_time_unit = rel_time_unit
        self.rel_time = rel_time
        self.rel_time_label = rel_time_label


class ObservationMetadata:
    def __init__(self, values: Dict[Modifier, Value]):
        """
        Metadata about an observation.
        For these metadata, modifiers need to be explicitly specified as keys.
        The metadata values are passed as observation value types.

        :param values: a map from modifier to the metadata value.
        """
        self.values = values


class Observation:
    def __init__(self,
                 patient: Patient,
                 concept: Concept,
                 visit: Optional[Visit],
                 trial_visit: TrialVisit,
                 start_date: Optional[date],
                 end_date: Optional[date],
                 value: Value,
                 metadata: Optional[ObservationMetadata] = None):
        """
        Data about an observed event or an attribute of a patient

        :param patient: the patient the event is observed about.
        :param concept: the concept defining the type of observations.
        :param visit: the (optional) visit when the observation was recorded.
        :param trial_visit: the trial visit the observation belongs to.
        :param start_date: the start date of the observation (N.B.: not the observed date,
                           e.g., birth date, that should be stored in the value field instead).
        :param end_date: the end date of the observations.
        :param value: the observed value.
        :param metadata: Metadata about the observations, e.g., a reason why data is missing,
                         the way of recording the data, a code of the sample on which the observation
                         was done.
        """
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
    Metadata tags, provided as a key-value dictionary.
    """
    def __init__(self, values: Dict[str, str]):
        self.values = values


class TreeNode:
    def __init__(self, name: str, metadata: Optional[TreeNodeMetadata] = None):
        """
        Ontology node

        Represents a node in the ontology.

        :param name: The name that appears in the ontology representation.
        :param metadata: a metadata dictionary of type TreeNodeMetadata.
        """
        self.parent: Optional['TreeNode'] = None
        self.name = name
        self.metadata = metadata
        self.children: Sequence['TreeNode'] = []

    def add_child(self, child: 'TreeNode'):
        """
        Add a child node to the ontology node.

        :param child: the child node.
        """
        self.children.append(child)


class StudyNode(TreeNode):
    def __init__(self, study: Study):
        """
        Study node

        Create an ontology node representing a study.

        :param study: the study.
        """
        TreeNode.__init__(self, study.name)
        self.study = study


class ConceptNode(TreeNode):
    def __init__(self, concept: Concept):
        """
        Concept node

        Create an ontology node representing a concept.

        :param concept: the concept.
        """

        TreeNode.__init__(self, concept.name)
        self.concept = concept


class DataCollection:
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
        """
        A data collection that can be loaded into TranSMART.
        Relation types and relations are optional, all other fields are mandatory.

        :param concepts: all concepts linked to observations and tree nodes.
        :param modifiers: all modifiers linked to observations and dimensions.
        :param dimensions: the extra dimensions, based on modifiers.
        :param studies: all studies linked to observations and tree nodes.
        :param trial_visits: all trial visits linked to observations.
        :param visits: all visits linked to observations.
        :param ontology: a list of root nodes of the ontology structure.
        :param patients: all subjects linked to observations and visits.
        :param observations: all observations in the data set.
        :param relation_types: all relation types linked to relations.
        :param relations: all relations in the data set, linked to subjects.
        """
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
