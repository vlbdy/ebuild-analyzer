from typing import List

from tree_sitter import Node

from ebuild_analyzer.ast.enums.node_types import NodeType


def find_closest_child_node_of_type(node_type: NodeType, node: Node) -> Node:
    for child in node.children:
        if child.type == node_type:
            return child
    raise RuntimeError(f"No child node of type '{node_type}' was found")


def get_command_name_from_command_node(command_node: Node) -> str:
    return find_closest_child_node_of_type(NodeType.COMMAND_NAME, command_node).text.decode()


def get_arguments_from_command_node(command_node: Node) -> List[str]:
    arguments = []
    for child in command_node.children:
        if child.type == NodeType.COMMAND_NAME:
            continue
        if child.type == NodeType.STRING or child.type == NodeType.RAW_STRING:
            # Remove the " or ' at the start and the end
            arguments.append(child.text.decode()[1:-1])
        else:
            arguments.append(child.text.decode())
    return arguments


def get_all_if_statement_condition_nodes(if_statement_node: Node) -> List[Node]:
    condition_nodes: List[Node] = []

    for child in if_statement_node.children:
        # End of condition nodes
        if child.type == NodeType.THEN:
            break
        condition_nodes.append(child)

    return condition_nodes
