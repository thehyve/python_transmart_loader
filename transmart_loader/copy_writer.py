import os
from datetime import date, datetime
from enum import Enum
from os import path
from typing import Set, Tuple, Dict, Optional

from transmart_loader.collection_validator import CollectionValidator
from transmart_loader.collection_visitor import CollectionVisitor
from transmart_loader.console import Console
from transmart_loader.loader_exception import LoaderException
from transmart_loader.transmart import DataCollection, Concept, Observation, \
    Patient, TreeNode, Visit, TrialVisit, \
    Study, ValueType, StudyNode, ConceptNode, Dimension
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


ValueTypeToVisualAttribute = {
    ValueType.Numeric: 'N',
    ValueType.Categorical: 'C',
    ValueType.Text: 'T',
    ValueType.Date: 'D'
}


study_dimension = Dimension('study', None, None)
concept_dimension = Dimension('concept', None, None)
patient_dimension = Dimension('patient', None, None)
start_time_dimension = Dimension('start time', None, None)
visit_dimension = Dimension('visit', None, None)


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


date_format = '%Y-%m-%d %H:%M:%S'


def format_date(value: Optional[date]) -> Optional[str]:
    if value is None:
        return None
    return value.strftime(date_format)


class TransmartCopyWriter(CollectionVisitor):
    """ Writes TranSMART data collections to a folder with files
    that can be loaded into a TranSMART database using transmart-copy.
    """

    concepts_header = ['concept_cd', 'concept_path', 'name_char']
    studies_header = ['study_num', 'study_id', 'secure_obj_token']
    dimensions_header = ['id', 'name', 'modifier_code', 'value_type']
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

    def visit_concept(self, concept: Concept) -> None:
        """ Serialises a Concept entity to a TSV file.

        :param concept: the Concept entity
        """
        if concept.concept_code not in self.concepts:
            row = [concept.concept_code, concept.concept_path, concept.name]
            self.concepts_writer.writerow(row)
            self.concepts.add(concept.concept_code)

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
            row = [study_index, study.study_id, 'PUBLIC']
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
        """ Serialises a Visit entity to a TSV file.
        NB: this requires all patient visits to be cleared before loading
        new visits for the patient.

        :param visit: the Visit entity
        """
        visit_key = (visit.patient.identifier, visit.identifier)
        if visit_key not in self.visits:
            row = [len(self.visits),
                   self.patients[visit.patient.identifier],
                   visit.active_status,
                   format_date(visit.start_date),
                   format_date(visit.end_date),
                   visit.inout,
                   visit.location,
                   None,
                   visit.length_of_stay,
                   None]
            self.visits_writer.writerow(row)
            self.visits[visit_key] = len(self.visits)

    def visit_tree_node(self, node: TreeNode, level=0, parent_path='\\'):
        """ Serialises a TreeNode entity and its children to a TSV file.

        :param node: the TreeNode entity
        :param level: the hierarchy level of the node
        :param parent_path: the path of the parent node.
        """
        node_path = parent_path + node.name + '\\'
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

    def visit_observation(self, observation: Observation) -> None:
        """ Serialises an Observation entity to a TSV file.

        FIXME: fix date value serialisation

        :param observation: the Observation entity
        """
        trial_visit_id = (observation.trial_visit.study.study_id,
                          observation.trial_visit.rel_time_label)
        visit_index = None
        if observation.visit:
            visit_key = (observation.patient.identifier,
                         observation.visit.identifier)
            visit_index = self.visits[visit_key]
        if visit_index is None:
            visit_index = -1
        value = observation.value
        text_value = None
        number_value = None
        blob_value = None
        value_type: ValueType = value.value_type()
        if value_type is ValueType.Numeric:
            number_value = value.value()
        elif value_type is ValueType.Date:
            if isinstance(value.value(), datetime):
                number_value = value.value().timestamp()
            else:
                date_value: date = value.value()
                datetime_value = datetime(
                    date_value.year, date_value.month, date_value.day)
                number_value = datetime_value.timestamp()
        elif value_type is ValueType.Categorical:
            text_value = value.value()
        elif value_type is ValueType.Text:
            blob_value = value.value()
        else:
            raise LoaderException(
                'Value type not supported: {}'.format(value.value_type))

        row = [visit_index,
               self.patients[observation.patient.identifier],
               observation.concept.concept_code,
               '@',
               observation.start_date,
               observation.end_date,
               '@',
               self.instance_num,
               self.trial_visits[trial_visit_id],
               TransmartCopyWriter.value_type_codes[value_type],
               text_value,
               number_value,
               blob_value]
        self.instance_num = self.instance_num + 1
        self.observations_writer.writerow(row)

    def write_dimension(self, dimension: Dimension) -> None:
        """ Serialises a Dimension entity to a TSV file.

        :param dimension: the Dimension entity
        """
        if dimension.name not in self.dimensions:
            value_type = None
            if dimension.value_type:
                value_type = TransmartCopyWriter.value_type_codes[
                    dimension.value_type]
            row = [len(self.dimensions),
                   dimension.name,
                   dimension.modifier_code,
                   value_type]
            self.dimensions_writer.writerow(row)
            self.dimensions[dimension.name] = len(self.dimensions)

    def write_dimensions(self) -> None:
        """ Write dimensions metadata and link all studies to the dimensions
        """
        dimensions = [
            study_dimension,
            concept_dimension,
            patient_dimension,
            start_time_dimension,
            visit_dimension
        ]
        for dimension in dimensions:
            self.write_dimension(dimension)

    def write_collection(self, collection: DataCollection) -> None:
        CollectionValidator.validate(collection)
        self.write_dimensions()
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
        self.visits_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/visit_dimension.tsv')
        self.visits_writer.writerow(self.visits_header)
        self.tree_nodes_writer = TsvWriter(
            self.output_dir + '/i2b2metadata/i2b2_secure.tsv')
        self.tree_nodes_writer.writerow(self.tree_nodes_header)
        self.observations_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/observation_fact.tsv')
        self.observations_writer.writerow(self.observations_header)

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.prepare_output_dir()
        self.concepts_writer: TsvWriter = None
        self.studies_writer: TsvWriter = None
        self.dimensions_writer: TsvWriter = None
        self.study_dimensions_writer: TsvWriter = None
        self.trial_visits_writer: TsvWriter = None
        self.patient_mappings_writer: TsvWriter = None
        self.patients_writer: TsvWriter = None
        self.visits_writer: TsvWriter = None
        self.tree_nodes_writer: TsvWriter = None
        self.observations_writer: TsvWriter = None
        self.init_writers()

        self.concepts: Set[str] = set()
        self.studies: Dict[str, int] = {}
        self.dimensions: Dict[str, int] = {}
        self.trial_visits: Dict[Tuple[str, str], int] = {}
        self.patients: Dict[str, int] = {}
        self.visits: Dict[Tuple[str, str], int] = {}
        self.paths: Set[str] = set()

        self.instance_num = 0
