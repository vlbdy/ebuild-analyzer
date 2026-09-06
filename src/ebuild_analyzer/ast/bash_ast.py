from re import Pattern
from typing import List, Optional

from tree_sitter import Tree, Node

from ebuild_analyzer.ast.enums.node_types import NodeType


class BashAST:
    def __init__(self, tree: Tree):
        self.__tree = tree

    def get_all_nodes_of_type(self, node_type: NodeType, pattern: Optional[Pattern[str]] = None) -> List[Node]:
        nodes: List[Node] = []

        def walk_and_save_nodes(node: Node) -> None:
            if node.type == node_type:
                if pattern is None or pattern.match(node.text.decode()):
                    nodes.append(node)

            for child in node.children:
                walk_and_save_nodes(child)

        walk_and_save_nodes(self.__tree.root_node)

        return nodes

    def get_tree(self) -> Tree:
        return self.__tree
