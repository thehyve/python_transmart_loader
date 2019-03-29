import os
from enum import Enum
from os import path
from typing import Set, Tuple, Dict

from transmart_loader.collection_validator import CollectionValidator
from transmart_loader.collection_visitor import CollectionVisitor
from transmart_loader.console import Console
from transmart_loader.loader_exception import LoaderException
from transmart_loader.transmart import DataCollection, Concept, Observation,\
    Patient, TreeNode, Visit, TrialVisit, \
    Study, ValueType, StudyNode, ConceptNode
from transmart_loader.tsv_writer import TsvWriter


class VisualAttribute(Enum):
    """
    Visual attribute of an ontology node
    """
    Leaf = 1,
    Folder = 2,
    Container = 3,
    Study = 4,
    Numerical = 5,
    Text = 6,
    Date = 7,
    Categorical = 8


ValueTypeToVisualAttribute = {
    ValueType.Numeric: 'N',
    ValueType.Categorical: 'C',
    ValueType.Text: 'T',
    ValueType.Date: 'D'
}


class TransmartCopyWriter(CollectionVisitor):
    """
    Writes TranSMART data collections to a folder with files
    that can be loaded into a TranSMART database using transmart-copy.

    FIXME: extend with writing dimension descriptions
    """

    concepts_header = ['concept_cd', 'concept_path', 'name_char']
    studies_header = ['study_num', 'study_id', 'secure_obj_token']
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
                           'modifier_cd',
                           'instance_num',
                           'trial_visit_num',
                           'valtype_cd',
                           'tval_char',
                           'nval_num',
                           'observation_blob']

    def visit_concept(self, concept: Concept) -> None:
        if concept.concept_code not in self.concepts:
            row = [concept.concept_code, concept.concept_path, concept.name]
            self.concepts_writer.writerow(row)
            self.concepts[concept.concept_code] = len(self.concepts)

    def visit_study(self, study: Study) -> None:
        if study.study_id not in self.studies:
            row = [len(self.studies), study.study_id, study.study_id]
            self.studies_writer.writerow(row)
            self.studies[study.study_id] = len(self.studies)

    def visit_trial_visit(self, trial_visit: TrialVisit) -> None:
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
        visit_key = (visit.patient.identifier, visit.identifier)
        if visit_key not in self.visits:
            row = [len(self.visits),
                   self.patients[visit.patient.identifier],
                   visit.active_status,
                   visit.start_date,
                   visit.end_date,
                   visit.inout,
                   visit.location,
                   None,
                   visit.length_of_stay,
                   None]
            self.visits_writer.writerow(row)
            self.visits[visit_key] = len(self.visits)

    def get_study_node_row(self, node: StudyNode, level, node_path):
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

    def get_concept_node_row(self, node: ConceptNode, level, node_path):
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

    def visit_tree_node(self, node: TreeNode, level, parent_path):
        path = parent_path + '\\' + node.name
        if isinstance(node, StudyNode):
            row = self.get_study_node_row(node, level, path)
        elif isinstance(node, ConceptNode):
            row = self.get_concept_node_row(node, level, path)
        else:
            raise LoaderException('Unsupported node type')
        if path not in self.paths:
            self.tree_nodes_writer.writerow(row)
            for child in node.children:
                self.visit_tree_node(child, level + 1, path)

    def visit_node(self, node: TreeNode) -> None:
        self.visit_tree_node(node, 0, '')

    def visit_patient(self, patient: Patient) -> None:
        if patient.identifier not in self.patients:
            patient_num = len(self.patients)
            patient_row = [patient_num, patient.sex]
            self.patients_writer.writerow(patient_row)
            patient_mapping_rows = [
                [patient.identifier, 'SUBJ_ID', patient_num]]
            for mapping in patient.mappings:
                if mapping.source is not 'SUBJ_ID':
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
        trial_visit_id = (observation.trial_visit.study.study_id,
                          observation.trial_visit.rel_time_label)
        value = observation.value
        text_value = None
        number_value = None
        blob_value = None
        value_type: ValueType = value.value_type()
        if value_type is ValueType.Numeric:
            number_value = value.value()
        elif value_type is ValueType.Date:
            number_value = value.value()
        elif value_type is ValueType.Categorical:
            text_value = value.value()
        elif value_type is ValueType.Text:
            blob_value = value.value()
        else:
            raise LoaderException(
                'Value type not supported: {}'.format(value.value_type))

        row = [-1,
               self.patients[observation.patient.identifier],
               observation.concept.concept_code,
               '@',
               observation.start_date,
               '@',
               self.instance_num,
               self.trial_visits[trial_visit_id],
               TransmartCopyWriter.value_type_codes[value_type],
               text_value,
               number_value,
               blob_value]
        self.instance_num = self.instance_num + 1
        self.observations_writer.writerow(row)

    def write_collection(self, collection: DataCollection) -> None:
        CollectionValidator.validate(collection)
        self.visit(collection)

    def prepare_output_dir(self):
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

    def init_writers(self):
        self.concepts_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/concept_dimension.tsv')
        self.concepts_writer.writerow(self.concepts_header)
        self.studies_writer = TsvWriter(
            self.output_dir + '/i2b2demodata/study.tsv')
        self.studies_writer.writerow(self.studies_header)
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
        self.trial_visits_writer: TsvWriter = None
        self.patient_mappings_writer: TsvWriter = None
        self.patients_writer: TsvWriter = None
        self.visits_writer: TsvWriter = None
        self.tree_nodes_writer: TsvWriter = None
        self.observations_writer: TsvWriter = None
        self.init_writers()

        self.concepts: Dict[str, int] = {}
        self.studies: Dict[str, int] = {}
        self.trial_visits: Dict[Tuple[str, str], int] = {}
        self.patients: Dict[str, int] = {}
        self.visits: Dict[Tuple[str, str], int] = {}
        self.paths: Set[str] = {}

        self.instance_num = 0
