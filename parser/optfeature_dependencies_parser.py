from typing import List

from tree_sitter import Node

from parser.optfeature import OptFeatureDependencies
from utils import ast_node_utils


class OptFeatureDependenciesParser:
    def parse_dependencies_recursively(self, optfeature_node: Node) -> OptFeatureDependencies:
        optfeature_dependencies = OptFeatureDependencies()

        current_node = optfeature_node.parent
        while current_node.type != "program":
            if current_node.type == "list":
                optfeature_dependencies += self.__parse_optfeature_list_parent(current_node)
            current_node = current_node.parent

        return optfeature_dependencies

    def __parse_optfeature_list_parent(self, list_parent: Node) -> OptFeatureDependencies:
        enabled_use_flag_dependencies: List[str] = []
        disabled_use_flag_dependencies: List[str] = []
        package_dependencies: List[str] = []

        for child in list_parent.children:
            if child.type == "command":
                command = ast_node_utils.get_command_name_from_command_node(child)
                arguments = ast_node_utils.get_arguments_from_command_node(child)
                if command == "use":
                    use_flag = arguments[0]
                    if use_flag.startswith('!'):
                        disabled_use_flag_dependencies.append(use_flag)
                    else:
                        enabled_use_flag_dependencies.append(use_flag)
                elif command == "has_version":
                    package_dependencies.append(arguments[0])

        return OptFeatureDependencies(enabled_use_flag_dependencies, disabled_use_flag_dependencies,
                                      package_dependencies)
