from tree_sitter import Node

from ebuild_analyzer.parser.optfeature import OptFeatureDependencies
from ebuild_analyzer.utils import ast_node_utils


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
        dependencies = OptFeatureDependencies()

        for child in list_parent.children:
            if child.type == "command":
                dependencies += self.__parse_command_dependency_node(child)
            elif child.type == "negated_command":
                command_node = ast_node_utils.find_closest_child_command_node(child)
                negated_dependencies = self.__parse_command_dependency_node(command_node)
                dependencies.negated_add(negated_dependencies)

        return dependencies

    def __parse_command_dependency_node(self, command_node: Node) -> OptFeatureDependencies:
        dependencies = OptFeatureDependencies()

        command = ast_node_utils.get_command_name_from_command_node(command_node)
        arguments = ast_node_utils.get_arguments_from_command_node(command_node)
        if command == "use":
            use_flag = arguments[0]
            if use_flag.startswith('!'):
                dependencies.disabled_use_flags.append(use_flag)
            else:
                dependencies.enabled_use_flags.append(use_flag)
        elif command == "has_version":
            dependencies.installed_packages.append(arguments[0])

        return dependencies
