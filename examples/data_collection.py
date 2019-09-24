from datetime import date, datetime
from tempfile import mkdtemp

from transmart_loader.copy_writer import TransmartCopyWriter
from transmart_loader.transmart import Concept, ValueType, Study, TrialVisit, Patient, Visit, \
    TreeNodeMetadata, ConceptNode, Observation, CategoricalValue, DateValue, DataCollection, NumericalValue, \
    TreeNode

# Create the dimension elements
age_concept = Concept('test:age', 'Age', '\\Test\\age',
                      ValueType.Numeric)
diagnosis_concept = Concept('test:diagnosis', 'Diagnosis', '\\Test\\diagnosis',
                            ValueType.Categorical)
diagnosis_date_concept = Concept('test:diagnosis_date', 'Diagnosis date', '\\Test\\diagnosis_date',
                                 ValueType.Date)
concepts = [age_concept, diagnosis_concept, diagnosis_date_concept]
studies = [Study('test', 'Test study')]
trial_visits = [
    TrialVisit(studies[0], 'Week 1', 'Week', 1)]
patients = [Patient('SUBJ0', 'male', []), Patient('SUBJ1', 'female', [])]
visits = [
    Visit(patients[0], 'visit1', None, None, None, None, None, None, []),
    Visit(patients[1], 'visit2', None, None, None, None, None, None, [])]
# Create the observations
observations = [
    Observation(patients[0], age_concept, visits[0], trial_visits[0],
                date(2019, 3, 28), None, NumericalValue(28)),
    Observation(patients[0], diagnosis_concept, visits[0], trial_visits[0],
                datetime(2019, 6, 26, 12, 34, 00),
                datetime(2019, 6, 28, 16, 46, 13, 345),
                CategoricalValue('Influenza')),
    Observation(patients[0], diagnosis_date_concept, visits[0], trial_visits[0],
                datetime(2019, 6, 26, 13, 50, 10), None,
                DateValue(datetime(2018, 4, 30, 17, 10, 00))),
    Observation(patients[1], age_concept, visits[1], trial_visits[0],
                date(2019, 3, 28), None, NumericalValue(43)),
    Observation(patients[1], diagnosis_concept, visits[1], trial_visits[0],
                datetime(2019, 8, 12, 10, 30, 00), None,
                CategoricalValue('Malaria')),
    Observation(patients[1], diagnosis_date_concept, visits[1], trial_visits[0],
                datetime(2019, 8, 12, 10, 30, 00), None,
                DateValue(datetime(2018, 10, 7, 13, 20, 00)))
]

# Create the ontology of the structure
# └ Ontology
#   ├ Age
#   ├ Diagnosis
#   └ Diagnosis date
top_node = TreeNode('Ontology')
top_node.metadata = TreeNodeMetadata(
    {'Upload date': str(date.today())})
top_node.add_child(ConceptNode(concepts[0]))
top_node.add_child(ConceptNode(concepts[1]))
top_node.add_child(ConceptNode(concepts[2]))
ontology = [top_node]

collection = DataCollection(concepts, [], [], studies,
                            trial_visits, visits, ontology, patients,
                            observations)

# Write collection to a temporary directory
# The generated files can be loaded into TranSMART with transmart-copy.
output_dir = mkdtemp()
print(f'Writing output to {output_dir} ...')
copy_writer = TransmartCopyWriter(output_dir)
copy_writer.write_collection(collection)
print('Done.')
