import shlex
from typing import List, Tuple

from tree_sitter import Node

from parser.optfeature import OptFeature, OptFeatureDependencies, PackageWithUses


def __parse_package_with_uses(package_string: str) -> PackageWithUses:
    # Package atoms can have USE flag requirements listed next to them within square brackets
    if '[' not in package_string:
        return PackageWithUses(package_string, None, None)

    start = package_string.index("[")
    end = package_string.index("]", start)

    package_name = package_string[:start]
    use_flags = package_string[start + 1:end].split(",")

    enabled_use_flags = []
    disabled_use_flags = []
    for use_flag in use_flags:
        if use_flag.startswith('-'):
            disabled_use_flags.append(use_flag[1:])
        else:
            enabled_use_flags.append(use_flag)

    return PackageWithUses(package_name, enabled_use_flags, disabled_use_flags)


def __remove_variables_from_package_string(package_string: str) -> str:
    # This parser does not support variable expansion, so they are removed
    if '$' not in package_string:
        return package_string
    return package_string[:package_string.index('$')]


def __remove_invalid_characters_from_package_string(package_string: str) -> str:
    # Usually after removing a variable from the end of a package string, the last character will be ':'
    # so it should be removed
    if package_string.endswith(':'):
        return package_string[:-1]
    return package_string


def __parse_optfeature_command(optfeature_command_text: str) -> Tuple[str, List[List[PackageWithUses]]]:
    _, description, *package_combinations = shlex.split(optfeature_command_text)

    package_combination_lists: List[List[PackageWithUses]] = []
    for package_combination in package_combinations:
        packages_with_uses: List[PackageWithUses] = []
        for package in package_combination.split(' '):
            package = __remove_variables_from_package_string(package)
            package = __remove_invalid_characters_from_package_string(package)
            packages_with_uses.append(__parse_package_with_uses(package))

        package_combination_lists.append(packages_with_uses)

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
