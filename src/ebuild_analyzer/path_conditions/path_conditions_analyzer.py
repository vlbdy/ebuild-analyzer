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
            path_conditions = self.__merge_path_conditions_with_multiple_and_conditions(path_conditions,
                                                                                        current_node_path_conditions)
            current_node = current_node.parent

        return path_conditions

    def __analyze_node_according_to_type(self, node: Node) -> List[PathCondition]:
        path_conditions: List[PathCondition] = []
        path_condition = PathCondition()

        if node.type == NodeType.COMMAND:
            path_condition += self.__analyze_command_node(node)

        elif node.type == NodeType.NEGATED_COMMAND:
            command_node = ast_node_utils.find_closest_child_node_of_type(NodeType.COMMAND, node)
            negated_path_conditions = self.__analyze_command_node(command_node)
            path_condition.negated_add(negated_path_conditions)

        elif node.type == NodeType.LIST:
            for child in node.children:
                if child.type == NodeType.OR and path_condition:
                    path_conditions.append(path_condition)
                    path_condition = PathCondition()

                current_node_path_conditions = self.__analyze_node_according_to_type(child)
                path_conditions.extend(
                    self.__merge_path_conditions_with_and_condition(path_condition, current_node_path_conditions))

        elif node.type == NodeType.IF_STATEMENT:
            for condition_node in ast_node_utils.get_all_if_statement_condition_nodes(node):
                if condition_node.type == NodeType.OR and path_condition:
                    path_conditions.append(path_condition)
                    path_condition = PathCondition()

                current_node_path_conditions = self.__analyze_node_according_to_type(condition_node)
                path_conditions.extend(
                    self.__merge_path_conditions_with_and_condition(path_condition, current_node_path_conditions))

        if path_condition:
            path_conditions.append(path_condition)
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

    def __merge_path_conditions_with_and_condition(self, and_condition: PathCondition,
                                                   path_conditions: List[PathCondition]) -> List[PathCondition]:
        merged_path_conditions = []
        for path_condition in path_conditions:
            merged_path_conditions.append(path_condition + and_condition)
        return merged_path_conditions

    def __merge_path_conditions_with_multiple_and_conditions(self, and_conditions: List[PathCondition],
                                                             path_conditions: List[PathCondition]) \
            -> List[PathCondition]:
        if not and_conditions:
            return path_conditions
        elif not path_conditions:
            return and_conditions

        merged_path_conditions = []
        for and_condition in and_conditions:
            merged_path_conditions.extend(
                self.__merge_path_conditions_with_and_condition(and_condition, path_conditions))
        return merged_path_conditions
