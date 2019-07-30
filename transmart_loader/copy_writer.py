import os
from datetime import date, datetime, timezone
from enum import Enum
from os import path
from typing import Set, Tuple, Dict, Optional

from transmart_loader.collection_validator import CollectionValidator
from transmart_loader.collection_visitor import CollectionVisitor
from transmart_loader.console import Console
from transmart_loader.loader_exception import LoaderException
from transmart_loader.transmart import DataCollection, Concept, Observation, \
    Patient, TreeNode, Visit, TrialVisit, Study, ValueType, StudyNode, \
    ConceptNode, Dimension, Modifier, Value, DimensionType, \
    Relation, RelationType, TreeNodeMetadata
from transmart_loader.tsv_writer import TsvWriter


class VisualAttribute(Enum):
    """
    Visual attribute of an ontology node
    """
    Leaf = 1
    Folder = 2
    Container = 3
    Study = 4
    Numerical = 5
    Text = 6
    Date = 7
    Categorical = 8


class TagKey:
    def __init__(self,
                 node_path: str,
                 tag_type: str):
        self.node_path = node_path
        self.tag_type = tag_type


ValueTypeToVisualAttribute = {
    ValueType.Numeric: 'N',
    ValueType.Categorical: 'C',
    ValueType.Text: 'T',
    ValueType.Date: 'D'
}


study_dimension = Dimension('study')
concept_dimension = Dimension('concept')
patient_dimension = Dimension('patient')
start_time_dimension = Dimension('start time')
visit_dimension = Dimension('visit')


def get_study_node_row(node: StudyNode, level, node_path):
    visual_attributes = '{}AS'.format(
        'L' if len(node.children) == 0 else 'F')
    row = [level,
           node_path,
           node.name,
           visual_attributes,
           None,
           '@',
           '@',
           '@',
           'T',
           '=',
           node.study.study_id,
           'PUBLIC']
    return row


def get_concept_node_row(node: ConceptNode, level, node_path):
    concept_type = ValueTypeToVisualAttribute[node.concept.value_type]
    visual_attributes = '{}A{}'.format(
        'L' if len(node.children) == 0 else 'F',
        concept_type)
    row = [level,
           node_path,
           node.name,
           visual_attributes,
           node.concept.concept_code,
           'CONCEPT_CD',
           'CONCEPT_DIMENSION',
           'CONCEPT_PATH',
           'T',
           'LIKE',
           node.concept.concept_path,
           'PUBLIC']
    return row


def get_tree_node_tag_row(tag_id: int,
                          node_path: str,
                          tag: str,
                          tag_type: str):
    row = [tag_id,
           node_path,
           tag,
           tag_type,
           1]
    return row


def get_folder_node_row(node: TreeNode, level, node_path):
    visual_attributes = 'CA '
    row = [level,
           node_path,
           node.name,
           visual_attributes,
           None,
           None,
           None,
           None,
           'T',
           'LIKE',
           '',
           'PUBLIC']
    return row


def to_utc(value: date) -> date:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def format_date(value: Optional[date]) -> Optional[str]:
    if value is None:
        return None
    return str(to_utc(value))


def microseconds(value: date) -> float:
    # numerical value is the timestamp in microseconds
    if isinstance(value, datetime):
        dt: datetime = datetime(value.year, value.month, value.day,
                                value.hour, value.minute, value.second,
                                tzinfo=timezone.utc)
    else:
        dt: datetime = datetime(value.year, value.month, value.day,
                                tzinfo=timezone.utc)
    return dt.timestamp() * 1000


def format_bool(value: Optional[bool]) -> Optional[str]:
    if value is None:
        return None
    return 't' if value else 'f'


class TransmartCopyWriter(CollectionVisitor):
    """ Writes TranSMART data collections to a folder with files
    that can be loaded into a TranSMART database using transmart-copy.
    """

    concepts_header = ['concept_cd', 'concept_path', 'name_char']
    modifiers_header = ['modifier_cd', 'modifier_path', 'name_char']
    studies_header = ['study_num',
                      'study_id',
                      'secure_obj_token',
                      'study_blob']
    dimensions_header = ['id',
                         'name',
                         'modifier_code',
                         'value_type',
                         'dimension_type',
                         'sort_index']
    study_dimensions_header = ['study_id', 'dimension_description_id']
    trial_visits_header = ['trial_visit_num',
                           'study_num',
                           'rel_time_unit_cd',
                           'rel_time_num',
                           'rel_time_label']
    patient_mappings_header = ['patient_ide',
                               'patient_ide_source',
                               'patient_num']
    patients_header = ['patient_num', 'sex_cd']
    encounter_mappings_header = ['encounter_ide',
                                 'encounter_ide_source',
                                 'encounter_num']
    visits_header = ['encounter_num',
                     'patient_num',
                     'active_status_cd',
                     'start_date',
                     'end_date',
                     'inout_cd',
                     'location_cd',
                     'location_path',
                     'length_of_stay',
                     'visit_blob']
    tree_nodes_header = ['c_hlevel',
                         'c_fullname',
                         'c_name',
                         'c_visualattributes',
                         'c_basecode',
                         'c_facttablecolumn',
                         'c_tablename',
                         'c_columnname',
                         'c_columndatatype',
                         'c_operator',
                         'c_dimcode',
                         'secure_obj_token']
    tree_node_tags_header = ['tag_id',
                             'path',
                             'tag',
                             'tag_type',
                             'tags_idx',
                             'tag_option_id']
    observations_header = ['encounter_num',
                           'patient_num',
                           'concept_cd',
                           'provider_id',
                           'start_date',
                           'end_date',
                           'modifier_cd',
                           'instance_num',
                           'trial_visit_num',
                           'valtype_cd',
                           'tval_char',
                           'nval_num',
                           'observation_blob']
    relation_types_header = ['id',
                             'label',
                             'description',
                             'symmetrical',
                             'biological']
    relations_header = ['left_subject_id',
                        'relation_type_id',
                        'right_subject_id',
                        'biological',
                        'share_household']

    def visit_concept(self, concept: Concept) -> None:
        """ Serialises a Concept entity to a TSV file.

        :param concept: the Concept entity
        """
        if concept.concept_code not in self.concepts:
            row = [concept.concept_code, concept.concept_path, concept.name]
            self.concepts_writer.writerow(row)
            self.concepts.add(concept.concept_code)

    def visit_modifier(self, modifier: Modifier) -> None:
        """ Serialises a Modifier entity to a TSV file.

        :param modifier: the Modifier entity
        """
        if modifier.modifier_code not in self.modifiers:
            row = [modifier.modifier_code,
                   modifier.modifier_path,
                   modifier.name]
            self.modifiers_writer.writerow(row)
            self.modifiers.add(modifier.modifier_code)

    def write_study_dimensions(self, study_index):
        for dimension_index in self.dimensions.values():
            study_dimension_row = [study_index, dimension_index]
            self.study_dimensions_writer.writerow(study_dimension_row)

    def visit_study(self, study: Study) -> None:
        """ Serialises a Study entity to a TSV file.

        :param study: the Study entity
        """
        if study.study_id not in self.studies:
            study_index = len(self.studies)
            row = [study_index, study.study_id, 'PUBLIC', study.metadata]
            self.studies_writer.writerow(row)
            self.studies[study.study_id] = study_index
            self.write_study_dimensions(study_index)

    def visit_trial_visit(self, trial_visit: TrialVisit) -> None:
        """ Serialises a TrialVisit entity to a TSV file.

        :param trial_visit: the TrialVisit entity
        """
        trial_visit_id = (trial_visit.study.study_id,
                          trial_visit.rel_time_label)
        if trial_visit_id not in self.trial_visits:
            row = [len(self.trial_visits),
                   self.studies[trial_visit.study.study_id],
                   trial_visit.rel_time_unit,
                   trial_visit.rel_time,
                   trial_visit.rel_time_label]
            self.trial_visits_writer.writerow(row)
            self.trial_visits[trial_visit_id] = len(self.trial_visits)

    def visit_visit(self, visit: Visit) -> None:
        """ Serialises a Visit entity and related EncounterMapping
        entities to a TSV file.

        :param visit: the Visit entity
        """
        if visit.identifier not in self.visits:
            encounter_num = len(self.visits)
            visit_row = [encounter_num,
                         self.patients[visit.patient.identifier],
                         visit.active_status,
                         format_date(visit.start_date),
                         format_date(visit.end_date),
                         visit.inout,
                         visit.location,
                         None,
                         visit.length_of_stay,
                         None]
            self.visits_writer.writerow(visit_row)
            encounter_mapping_rows = [
                [visit.identifier, 'VISIT_ID', encounter_num]]
            for mapping in visit.mappings:
                if mapping.source != 'VISIT_ID':
                    encounter_mapping_rows.append(
                        [mapping.identifier, mapping.source, encounter_num])
            self.encounter_mappings_writer.writerows(encounter_mapping_rows)
            self.visits[visit.identifier] = encounter_num

    def write_tree_node_tags(self, metadata: TreeNodeMetadata, node_path: str):
        for tag_type, tag in metadata.values.items():
            tag_key = TagKey(node_path, tag_type)
            if tag_key not in self.tags:
                tag_id = len(self.tags)
                row = get_tree_node_tag_row(tag_id, node_path, tag, tag_type)
                self.tree_node_tags_writer.writerow(row)
                self.tags.add(TagKey(node_path, tag_type))

    def visit_tree_node(self, node: TreeNode, level=0, parent_path='\\'):
        """ Serialises a TreeNode entity and its children to a TSV file.

        :param node: the TreeNode entity
        :param level: the hierarchy level of the node
        :param parent_path: the path of the parent node.
        """
        node_path = parent_path + node.name + '\\'

        if node.metadata:
            self.write_tree_node_tags(node.metadata, node_path)

        if isinstance(node, StudyNode):
            row = get_study_node_row(node, level, node_path)
        elif isinstance(node, ConceptNode):
            row = get_concept_node_row(node, level, node_path)
        elif len(node.children) > 0:
            row = get_folder_node_row(node, level, node_path)
        else:
            Console.warning('Skipping node {}'.format(node_path))
            return
        if node_path not in self.paths:
            if len(node_path) > 900:
                Console.warning("Path too long: " + node_path)
            self.tree_nodes_writer.writerow(row)
            self.paths.add(node_path)
            for child in node.children:
                self.visit_tree_node(child, level + 1, node_path)

    def visit_node(self, node: TreeNode) -> None:
        self.visit_tree_node(node)

    def visit_patient(self, patient: Patient) -> None:
        """ Serialises an Patient entity and related PatientMapping
        entities to TSV files.

        :param patient: the Patient entity
        """
        if patient.identifier not in self.patients:
            patient_num = len(self.patients)
            patient_row = [patient_num, patient.sex]
            self.patients_writer.writerow(patient_row)
            patient_mapping_rows = [
                [patient.identifier, 'SUBJ_ID', patient_num]]
            for mapping in patient.mappings:
                if mapping.source != 'SUBJ_ID':
                    patient_mapping_rows.append(
                        [mapping.identifier, mapping.source, patient_num])
            self.patient_mappings_writer.writerows(patient_mapping_rows)
            self.patients[patient.identifier] = patient_num

    value_type_codes = {
        ValueType.Numeric: 'N',
        ValueType.Categorical: 'T',
        ValueType.Date: 'D',
        ValueType.Text: 'B'
    }

    def write_observation(self,
                          observation: Observation,
                          value: Value,
                          modifier: Modifier = None) -> None:
        trial_visit_id = (observation.trial_visit.study.study_id,
                          observation.trial_visit.rel_time_label)
        visit_index = None
        if observation.visit:
            visit_index = self.visits[observation.visit.identifier]
        if visit_index is None:
            visit_index = -1
        text_value = None
        number_value = None
        blob_value = None
        value_type: ValueType = value.value_type
        if value_type is ValueType.Numeric:
            number_value = value.value
        elif value_type is ValueType.Date:
            if value.value:
                if not isinstance(value.value, date):
                    raise LoaderException(
                        'Invalid date type: {}'.format(type(value.value)))
                number_value = microseconds(value.value)
        elif value_type is ValueType.Categorical:
            text_value = value.value
        elif value_type is ValueType.Text:
            blob_value = value.value
        else:
            raise LoaderException(
                'Value type not supported: {}'.format(value.value_type))

        row = [visit_index,
               self.patients[observation.patient.identifier],
               observation.concept.concept_code,
               '@',
               format_date(observation.start_date),
               format_date(observation.end_date),
               modifier.modifier_code if modifier else '@',
               self.instance_num,
               self.trial_visits[trial_visit_id],
               TransmartCopyWriter.value_type_codes[value_type],
               text_value,
               number_value,
               blob_value]
        self.observations_writer.writerow(row)

    def visit_observation(self, observation: Observation) -> None:
        """ Serialises an Observation entity to a TSV file.

        :param observation: the Observation entity
        """
        self.write_observation(observation, observation.value)
        if observation.metadata:
            for modifier, value in observation.metadata.values.items():
                self.write_observation(observation, value, modifier)
        self.instance_num = self.instance_num + 1

    def visit_relation_type(self, relation_type: RelationType) -> None:
        """ Serialises a relation type to a TSV file.

        :param relation_type: the relation type
        """
        if relation_type.label not in self.relation_types:
            relation_type_index = len(self.relation_types)
            row = [relation_type_index,
                   relation_type.label,
                   relation_type.description,
                   format_bool(relation_type.symmetrical),
                   format_bool(relation_type.biological)]
            self.relation_types_writer.writerow(row)
            self.relation_types[relation_type.label] = relation_type_index

    def visit_relation(self, relation: Relation) -> None:
        """ Serialises a Relation entity to a TSV file.

        :param relation: the Relation entity
        """
        row = [self.patients[relation.left.identifier],
               self.relation_types[relation.relation_type.label],
               self.patients[relation.right.identifier],
               format_bool(relation.biological),
               format_bool(relation.share_household)]
        self.relations_writer.writerow(row)

    def visit_dimension(self, dimension: Dimension) -> None:
        """ Serialises a Dimension entity to a TSV file.

        :param dimension: the Dimension entity
        """
        if dimension.name not in self.dimensions:
            value_type = None
            if dimension.modifier and dimension.modifier.value_type:
                value_type = TransmartCopyWriter.value_type_codes[
                    dimension.modifier.value_type]
            dimension_type: Optional[str] = None
            if dimension.dimension_type == DimensionType.Subject:
                dimension_type = 'SUBJECT'
            row = [len(self.dimensions),
                   dimension.name,
                   dimension.modifier.modifier_code
                   if dimension.modifier else None,
                   value_type,
                   dimension_type,
                   dimension.sort_index]
            self.dimensions_writer.writerow(row)
            self.dimensions[dimension.name] = len(self.dimensions)

    def write_default_dimensions(self) -> None:
        """ Write dimensions metadata and link all studies to the dimensions
        """
        default_dimensions = [
            study_dimension,
            concept_dimension,
            patient_dimension,
            start_time_dimension,
            visit_dimension
        ]
        for dimension in default_dimensions:
            self.visit_dimension(dimension)

    def write_collection(self, collection: DataCollection) -> None:
        CollectionValidator.validate(collection)
        self.write_default_dimensions()
        self.visit(collection)

    def prepare_output_dir(self) -> None:
        """ Creates an output directory if it does not exist.
        Fails if the output directory exists and is not empty.
        """
        output_dir = self.output_dir
        if not path.exists(output_dir):
            Console.info('Creating output directory: {}'.format(output_dir))
            os.makedirs(output_dir, 0o0700, True)
        if not path.isdir(output_dir):
            raise LoaderException(
                'Path is not a directory: {}'.format(output_dir))
        if os.listdir(output_dir):
            raise LoaderException(
                'Directory is not empty: {}'.format(output_dir))
        os.mkdir(output_dir + '/i2b2metadata')
        os.mkdir(output_dir + '/i2b2demodata')

    def init_writers(self) -> None:
        """ Creates files and initialises writers for the output files
        in transmart-copy format.
        """
        self.concepts_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/concept_dimension.tsv')
        self.concepts_writer.writerow(self.concepts_header)
        self.modifiers_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/modifier_dimension.tsv')
        self.modifiers_writer.writerow(self.modifiers_header)
        self.studies_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/study.tsv')
        self.studies_writer.writerow(self.studies_header)
        self.dimensions_writer = TsvWriter(
            self.output_dir + '/i2b2metadata/dimension_description.tsv')
        self.dimensions_writer.writerow(self.dimensions_header)
        self.study_dimensions_writer = TsvWriter(
            self.output_dir + '/i2b2metadata/study_dimension_descriptions.tsv')
        self.study_dimensions_writer.writerow(self.study_dimensions_header)
        self.trial_visits_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/trial_visit_dimension.tsv')
        self.trial_visits_writer.writerow(self.trial_visits_header)
        self.patient_mappings_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/patient_mapping.tsv')
        self.patient_mappings_writer.writerow(self.patient_mappings_header)
        self.patients_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/patient_dimension.tsv')
        self.patients_writer.writerow(self.patients_header)
        self.encounter_mappings_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/encounter_mapping.tsv')
        self.encounter_mappings_writer.writerow(self.encounter_mappings_header)
        self.visits_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/visit_dimension.tsv')
        self.visits_writer.writerow(self.visits_header)
        self.tree_nodes_writer = TsvWriter(
            self.output_dir + '/i2b2metadata/i2b2_secure.tsv')
        self.tree_nodes_writer.writerow(self.tree_nodes_header)
        self.tree_node_tags_writer = TsvWriter(
            self.output_dir + '/i2b2metadata/i2b2_tags.tsv')
        self.tree_node_tags_writer.writerow(self.tree_node_tags_header)
        self.observations_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/observation_fact.tsv')
        self.observations_writer.writerow(self.observations_header)
        self.relation_types_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/relation_types.tsv')
        self.relation_types_writer.writerow(self.relation_types_header)
        self.relations_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/relations.tsv')
        self.relations_writer.writerow(self.relations_header)

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.prepare_output_dir()
        self.concepts_writer: TsvWriter = None
        self.modifiers_writer: TsvWriter = None
        self.studies_writer: TsvWriter = None
        self.dimensions_writer: TsvWriter = None
        self.study_dimensions_writer: TsvWriter = None
        self.trial_visits_writer: TsvWriter = None
        self.patient_mappings_writer: TsvWriter = None
        self.patients_writer: TsvWriter = None
        self.encounter_mappings_writer: TsvWriter = None
        self.visits_writer: TsvWriter = None
        self.tree_nodes_writer: TsvWriter = None
        self.tree_node_tags_writer: TsvWriter = None
        self.observations_writer: TsvWriter = None
        self.relation_types_writer: TsvWriter = None
        self.relations_writer: TsvWriter = None
        self.init_writers()

        self.concepts: Set[str] = set()
        self.modifiers: Set[str] = set()
        self.dimensions: Dict[str, int] = {}
        self.studies: Dict[str, int] = {}
        self.trial_visits: Dict[Tuple[str, str], int] = {}
        self.patients: Dict[str, int] = {}
        self.relation_types: Dict[str, int] = {}
        self.visits: Dict[str, int] = {}
        self.paths: Set[str] = set()
        self.tags: Set[TagKey] = set()

        self.instance_num = 0
