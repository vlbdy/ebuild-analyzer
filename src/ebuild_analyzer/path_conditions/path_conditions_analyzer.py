from typing import List

from tree_sitter import Node

from ebuild_analyzer.ast import ast_node_utils
from ebuild_analyzer.ast.enums.command import Command
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.package_atoms.package_atom_parser import PackageAtomParser
from ebuild_analyzer.path_conditions.path_condition import PathCondition


class PathConditionsAnalyzer:
    def __init__(self):
        self.__package_atom_parser = PackageAtomParser()

        self.__original_node = None  # Used during analysis to avoid using the original node as a path condition
        self.__is_in_else_clause = False  # Also used during analysis internally

    def analyze(self, node: Node) -> List[PathCondition]:
        path_conditions: List[PathCondition] = []
        self.__original_node = node

        current_node = node.parent
        while current_node.type != NodeType.PROGRAM:
            current_node_path_conditions = self.__analyze_node_according_to_type(current_node)
            path_conditions = self.__combine_conditions(path_conditions, current_node_path_conditions)

            # We must skip the parent of an `elif_clause` because it is the first if statement. The if statement
            # is irrelevant since we were in the elif clause therefore we skip it.
            if current_node.type == NodeType.ELIF_CLAUSE:
                current_node = current_node.parent

            current_node = current_node.parent

        return path_conditions

    def __analyze_node_according_to_type(self, node: Node) -> List[PathCondition]:
        if node == self.__original_node:
            return []

        if node.type == NodeType.ELSE_CLAUSE:
            self.__is_in_else_clause = True

        if ast_node_utils.is_command_node(node):
            return [self.__analyze_simple_node(node)]
        elif ast_node_utils.is_compound_node(node):
            conditions = self.__analyze_compound_node(node)

            # Only if statements can have else clauses, so they are handled here
            if self.__is_in_else_clause:
                self.__is_in_else_clause = False
                return self.__negate_path_conditions(conditions)
            else:
                return conditions
        else:
            return []

    def __analyze_simple_node(self, node: Node) -> PathCondition:
        path_condition = PathCondition()

        if node.type == NodeType.COMMAND:
            path_condition += self.__analyze_command_node(node)

        elif node.type == NodeType.NEGATED_COMMAND:
            command_node = ast_node_utils.find_closest_direct_child_node_of_type(NodeType.COMMAND, node)
            negated_path_conditions = self.__analyze_command_node(command_node)
            path_condition.negated_add(negated_path_conditions)

        return path_condition

    def __analyze_compound_node(self, node: Node) -> List[PathCondition]:
        condition_nodes: List[Node] = []
        if node.type == NodeType.LIST:
            condition_nodes = node.children
        elif node.type in (NodeType.IF_STATEMENT, NodeType.ELIF_CLAUSE):
            condition_nodes = ast_node_utils.get_all_condition_nodes(node)

        path_conditions: List[PathCondition] = []

        last_node_type = NodeType.PROGRAM  # Placeholder
        for condition_node in condition_nodes:
            new_path_conditions = self.__analyze_node_according_to_type(condition_node)
            if last_node_type == NodeType.AND:
                path_conditions = self.__combine_conditions(path_conditions, new_path_conditions)
            else:
                path_conditions.extend(new_path_conditions)
                # This check is specifically for cases where an optfeature command follows a condition like:
                #   has_version ... || optfeature ...
                # In this case, the optfeature is advertised if the condition is *not* met, therefore we must negate it.
                if self.__is_optfeature_command_node(condition_node):
                    path_conditions = self.__negate_path_conditions(path_conditions)
            last_node_type = condition_node.type

        return path_conditions

    def __analyze_command_node(self, command_node: Node) -> PathCondition:
        path_conditions = PathCondition()

        command = ast_node_utils.get_command_name_from_command_node(command_node)
        arguments = ast_node_utils.get_arguments_from_command_node(command_node)
        if command == Command.USE:
            use_flag = arguments[0]
            if use_flag.startswith('!'):
                path_conditions.disabled_use_flags.add(use_flag[1:])
            else:
                path_conditions.enabled_use_flags.add(use_flag)
        elif command == Command.HAS_VERSION:
            path_conditions.installed_packages.add(self.__package_atom_parser.parse(arguments[0]))
        else:
            path_conditions.successful_commands.add(command_node.text.decode())

        return path_conditions

    def __combine_conditions(self, first: List[PathCondition], second: List[PathCondition]) \
            -> List[PathCondition]:
        if not first:
            return second.copy()
        if not second:
            return first.copy()

        return [first_condition + second_condition for first_condition in first for second_condition in second]

    def __is_optfeature_command_node(self, node: Node) -> bool:
        if node.type == NodeType.COMMAND:
            return self.__does_command_node_refer_to_optfeature(node)
        elif node.type == NodeType.NEGATED_COMMAND:
            command_node = ast_node_utils.find_closest_direct_child_node_of_type(NodeType.COMMAND, node)
            return self.__does_command_node_refer_to_optfeature(command_node)
        else:
            return False

    def __does_command_node_refer_to_optfeature(self, command_node: Node) -> bool:
        command = ast_node_utils.get_command_name_from_command_node(command_node)
        return command.startswith(Command.OPTFEATURE) and not command.startswith(Command.OPTFEATURE_HEADER)

    def __negate_path_conditions(self, conditions: List[PathCondition]) -> List[PathCondition]:
        new_conditions: List[PathCondition] = []
        for condition in conditions:
            new_conditions = self.__combine_conditions(condition.negate(), new_conditions)
        return new_conditions
