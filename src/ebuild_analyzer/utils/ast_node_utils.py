from typing import List

from tree_sitter import Node


def find_closest_child_command_node(node: Node) -> Node:
    for child in node.children:
        if child.type == "command":
            return child
    raise RuntimeError("Command node not found")


def get_command_name_from_command_node(command_node: Node) -> str:
    for child in command_node.children:
        if child.type == "command_name":
            return child.text.decode()
    raise RuntimeError("No command_name child under node")


def get_arguments_from_command_node(command_node: Node) -> List[str]:
    arguments = []
    for child in command_node.children:
        if child.type == "command_name":
            continue
        if child.type == "string" or child.type == "raw_string":
            # Remove the " or ' at the start and the end
            arguments.append(child.text.decode()[1:-1])
        else:
            arguments.append(child.text.decode())
    return arguments


def get_all_if_statement_condition_nodes(if_statement_node: Node) -> List[Node]:
    condition_nodes: List[Node] = []

    for child in if_statement_node.children:
        # End of condition nodes
        if child.type == "then":
            break
        condition_nodes.append(child)

    return condition_nodes
