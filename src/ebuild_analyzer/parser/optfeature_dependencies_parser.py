from tree_sitter import Node

from ebuild_analyzer.parser.optfeature import OptFeatureDependencies
from ebuild_analyzer.utils import ast_node_utils


class OptFeatureDependenciesParser:
    def parse(self, optfeature_node: Node) -> OptFeatureDependencies:
        optfeature_dependencies = OptFeatureDependencies()

        current_node = optfeature_node.parent
        while current_node.type != "program":
            optfeature_dependencies += self.__parse_node_according_to_type(current_node)
            current_node = current_node.parent

        return optfeature_dependencies

    def __parse_node_according_to_type(self, node: Node) -> OptFeatureDependencies:
        dependencies = OptFeatureDependencies()
        if node.type == "command":
            dependencies += self.__parse_command_node(node)
        elif node.type == "negated_command":
            command_node = ast_node_utils.find_closest_child_node_of_type("command", node)
            negated_dependencies = self.__parse_command_node(command_node)
            dependencies.negated_add(negated_dependencies)
        elif node.type == "list":
            for child in node.children:
                dependencies += self.__parse_node_according_to_type(child)
        elif node.type == "if_statement":
            for condition_node in ast_node_utils.get_all_if_statement_condition_nodes(node):
                dependencies += self.__parse_node_according_to_type(condition_node)
        return dependencies

    def __parse_command_node(self, command_node: Node) -> OptFeatureDependencies:
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
