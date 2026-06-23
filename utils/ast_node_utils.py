from typing import List

from tree_sitter import Node


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
