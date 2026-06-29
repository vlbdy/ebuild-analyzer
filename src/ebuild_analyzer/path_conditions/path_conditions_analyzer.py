from typing import List

from tree_sitter import Node

from ebuild_analyzer.ast import ast_node_utils
from ebuild_analyzer.ast.enums.command import Command
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.path_conditions.path_condition import PathCondition


class PathConditionsAnalyzer:
    def analyze(self, node: Node) -> List[PathCondition]:
        path_conditions: List[PathCondition] = []

        current_node = node.parent
        while current_node.type != NodeType.PROGRAM:
            current_node_path_conditions = self.__analyze_node_according_to_type(current_node)
            path_conditions = self.__combine_conditions(path_conditions, current_node_path_conditions)
            current_node = current_node.parent

        return path_conditions

    def __analyze_node_according_to_type(self, node: Node) -> List[PathCondition]:
        if ast_node_utils.is_command_node(node):
            return [self.__analyze_simple_node(node)]
        elif ast_node_utils.is_compound_node(node):
            return self.__analyze_compound_node(node)
        else:
            return []

    def __analyze_simple_node(self, node: Node) -> PathCondition:
        path_condition = PathCondition()

        if node.type == NodeType.COMMAND:
            path_condition += self.__analyze_command_node(node)

        elif node.type == NodeType.NEGATED_COMMAND:
            command_node = ast_node_utils.find_closest_child_node_of_type(NodeType.COMMAND, node)
            negated_path_conditions = self.__analyze_command_node(command_node)
            path_condition.negated_add(negated_path_conditions)

        return path_condition

    def __analyze_compound_node(self, node: Node) -> List[PathCondition]:
        condition_nodes: List[Node] = []
        if node.type == NodeType.LIST:
            condition_nodes = node.children
        elif node.type == NodeType.IF_STATEMENT:
            condition_nodes = ast_node_utils.get_all_if_statement_condition_nodes(node)

        path_conditions: List[PathCondition] = []

        last_node_type = NodeType.PROGRAM  # Placeholder
        for condition_node in condition_nodes:
            new_path_conditions = self.__analyze_node_according_to_type(condition_node)
            if last_node_type == NodeType.AND:
                path_conditions = self.__combine_conditions(path_conditions, new_path_conditions)
            else:
                path_conditions.extend(new_path_conditions)
            last_node_type = condition_node.type

        return path_conditions

    def __analyze_command_node(self, command_node: Node) -> PathCondition:
        path_conditions = PathCondition()

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

    def __combine_conditions(self, first: List[PathCondition], second: List[PathCondition]) \
            -> List[PathCondition]:
        if not first:
            return second.copy()
        if not second:
            return first.copy()

        return [first_condition + second_condition for first_condition in first for second_condition in second]
