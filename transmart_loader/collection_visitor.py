from abc import abstractmethod
from typing import Optional

from transmart_loader.transmart import DataCollection, Concept, Patient, \
    Observation, TreeNode, Visit, TrialVisit, Study, Modifier, Dimension, \
    Relation, RelationType


class CollectionVisitor:
    """
    Visitor class for TranSMART data collections
    """

    @abstractmethod
    def visit_concept(self, concept: Concept) -> None:
        pass

    @abstractmethod
    def visit_modifier(self, modifier: Modifier) -> None:
        pass

    @abstractmethod
    def visit_dimension(self, dimension: Dimension) -> None:
        pass

    @abstractmethod
    def visit_study(self, study: Study) -> None:
        pass

    @abstractmethod
    def visit_trial_visit(self, trial_visit: TrialVisit) -> None:
        pass

    @abstractmethod
    def visit_visit(self, visit: Visit) -> None:
        pass

    @abstractmethod
    def visit_node(self, node: TreeNode) -> None:
        pass

    @abstractmethod
    def visit_patient(self, patient: Patient) -> None:
        pass

    @abstractmethod
    def visit_observation(self, observation: Observation) -> None:
        pass

    @abstractmethod
    def visit_relation_type(self, relation_type: RelationType) -> None:
        pass

    @abstractmethod
    def visit_relation(self, relation: Relation) -> None:
        pass

    def visit(self, collection: Optional[DataCollection]) -> None:
        if collection is None:
            return
        for concept in collection.concepts:
            self.visit_concept(concept)
        for modifier in collection.modifiers:
            self.visit_modifier(modifier)
        for dimension in collection.dimensions:
            self.visit_dimension(dimension)
        for study in collection.studies:
            self.visit_study(study)
        for trial_visit in collection.trial_visits:
            self.visit_trial_visit(trial_visit)
        for patient in collection.patients:
            self.visit_patient(patient)
        for visit in collection.visits:
            self.visit_visit(visit)
        for node in collection.ontology:
            self.visit_node(node)
        for observation in collection.observations:
            self.visit_observation(observation)
        for relation_type in collection.relation_types:
            self.visit_relation_type(relation_type)
        for relation in collection.relations:
            self.visit_relation(relation)
