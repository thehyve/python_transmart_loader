from typing import Dict, Set

from transmart_loader.transmart import TreeNode, ConceptNode, Concept, ValueType


class OntologyMapper:
    """
    Map ontology nodes to TranSMART
    """
    def __init__(self, system: str):
        self.system = system
        self.chapter_nodes: Dict[str, TreeNode] = {}
        self.group_nodes: Dict[str, TreeNode] = {}
        self.concepts: Set[Concept] = set()

    def map_chapter(self, code: str, name: str) -> None:
        node = TreeNode('{} {}'.format(code, name))
        self.chapter_nodes[code] = node

    def map_group(self, range_start: str, range_end: str, chapter: str, name: str) -> None:
        node = TreeNode('{}-{} {}'.format(range_start, range_end, name))
        self.group_nodes[range_start] = node
        chapter_node = self.chapter_nodes[chapter]
        chapter_node.add_child(node)

    def map_subgroup(self, group: str, code: str, name: str) -> None:
        node = TreeNode('{} {}'.format(code, name))
        group_node = self.group_nodes[group]
        group_node.add_child(node)
        self.group_nodes[code] = node

    def map_code(self, group: str, code: str, name: str) -> None:
        concept = Concept(code, name, self.system + '/' + code, ValueType.Categorical)
        self.concepts.add(concept)
        node = ConceptNode(concept)
        if '.' in code:
            parent_group_code = code[:-1] + '-'
            parent_node = self.group_nodes[parent_group_code]
        else:
            parent_node = self.group_nodes[group]
        parent_node.add_child(node)
