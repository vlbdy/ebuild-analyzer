from tree_sitter import Node

from ebuild_analyzer.ast import ast_node_utils
from ebuild_analyzer.ast.enums.command import Command
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.path_conditions.path_conditions import PathConditions


class PathConditionsAnalyzer:
    def analyze(self, node: Node) -> PathConditions:
        path_conditions = PathConditions()

        current_node = node.parent
        while current_node.type != NodeType.PROGRAM:
            path_conditions += self.__analyze_node_according_to_type(current_node)
            current_node = current_node.parent

        return path_conditions

    def __analyze_node_according_to_type(self, node: Node) -> PathConditions:
        path_conditions = PathConditions()
        if node.type == NodeType.COMMAND:
            path_conditions += self.__analyze_command_node(node)
        elif node.type == NodeType.NEGATED_COMMAND:
            command_node = ast_node_utils.find_closest_child_node_of_type(NodeType.COMMAND, node)
            negated_path_conditions = self.__analyze_command_node(command_node)
            path_conditions.negated_add(negated_path_conditions)
        elif node.type == NodeType.LIST:
            for child in node.children:
                path_conditions += self.__analyze_node_according_to_type(child)
        elif node.type == NodeType.IF_STATEMENT:
            for condition_node in ast_node_utils.get_all_if_statement_condition_nodes(node):
                path_conditions += self.__analyze_node_according_to_type(condition_node)
        return path_conditions

    def __analyze_command_node(self, command_node: Node) -> PathConditions:
        path_conditions = PathConditions()

        command = ast_node_utils.get_command_name_from_command_node(command_node)
        arguments = ast_node_utils.get_arguments_from_command_node(command_node)
        if command == Command.USE:
            use_flag = arguments[0]
            if use_flag.startswith('!'):
                path_conditions.disabled_use_flags.append(use_flag)
            else:
                path_conditions.enabled_use_flags.append(use_flag)
        elif command == Command.HAS_VERSION:
            path_conditions.installed_packages.append(arguments[0])

        return path_conditions
