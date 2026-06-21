from typing import List

from tree_sitter import Tree, Node


class EbuildAST:
    def __init__(self, tree: Tree):
        self.__tree = tree

    def get_all_optfeature_nodes(self) -> List[Node]:
        optfeature_nodes: List[Node] = []

        def walk_and_save_optfeature_nodes(node: Node) -> None:
            if node.type == "command" and node.text.startswith(b"optfeature"):
                optfeature_nodes.append(node)
            for child in node.children:
                walk_and_save_optfeature_nodes(child)

        walk_and_save_optfeature_nodes(self.__tree.root_node)

        return optfeature_nodes
