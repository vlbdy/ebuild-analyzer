import shlex
from typing import List, Tuple

from tree_sitter import Node

from parser.optfeature import OptFeature, OptFeatureDependencies


def __parse_optfeature_command(optfeature_command_text: str) -> Tuple[str, List[List[str]]]:
    _, description, *package_combinations = shlex.split(optfeature_command_text)

    package_combination_lists = []
    for package_combination in package_combinations:
        package_combination_lists.append(package_combination.split(' '))

    return description, package_combination_lists


def __parse_optfeature_list_parent(list_parent: Node) -> OptFeatureDependencies:
    enabled_use_flag_dependencies: List[str] = []
    disabled_use_flag_dependencies: List[str] = []
    package_dependencies: List[str] = []

    for child in list_parent.children:
        text = child.text.decode()
        if text.startswith("use"):
            use_flag = shlex.split(text)[1]
            if use_flag.startswith('!'):
                disabled_use_flag_dependencies.append(use_flag[1:])
            else:
                enabled_use_flag_dependencies.append(use_flag)
        elif text.startswith("has_version"):
            package_dependencies.append(shlex.split(text)[1])

    return OptFeatureDependencies(enabled_use_flag_dependencies, disabled_use_flag_dependencies, package_dependencies)


def parse_single_optfeature_node(optfeature_ast_node: Node, header: str) -> OptFeature:
    description, package_combinations = __parse_optfeature_command(optfeature_ast_node.text.decode())
    optfeature_dependencies = None

    current_node = optfeature_ast_node.parent
    while current_node.type != "program":
        if current_node.type == "list":
            optfeature_dependencies = __parse_optfeature_list_parent(current_node)
        current_node = current_node.parent

    return OptFeature(optfeature_dependencies, header, description, package_combinations)


def parse_multiple_optfeature_nodes(optfeature_ast_nodes: List[Node]) -> List[OptFeature]:
    current_header = None
    optfeatures: List[OptFeature] = []

    for node in optfeature_ast_nodes:
        if node.text.startswith(b"optfeature_header"):
            command_elements = shlex.split(node.text.decode())
            if len(command_elements) > 1:
                current_header = command_elements[1]
        else:
            optfeatures.append(parse_single_optfeature_node(node, current_header))

    return optfeatures
