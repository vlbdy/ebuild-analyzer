import re
from typing import List, Tuple

from tree_sitter import Node

from ebuild_analyzer.ast import ast_node_utils
from ebuild_analyzer.ast.enums.command import Command
from ebuild_analyzer.extractors.optfeature import OptFeature, PackageWithUses
from ebuild_analyzer.path_conditions.path_conditions_analyzer import PathConditionsAnalyzer


class OptFeaturesExtractor:
    def __init__(self):
        self.__conditions_analyzer = PathConditionsAnalyzer()

    def extract(self, optfeature_ast_nodes: List[Node]) -> List[OptFeature]:
        current_header = None
        optfeatures: List[OptFeature] = []

        for node in optfeature_ast_nodes:
            if node.text.decode().startswith(Command.OPTFEATURE_HEADER):
                header_arguments = ast_node_utils.get_arguments_from_command_node(node)
                current_header = header_arguments[0] if header_arguments else None
            else:
                optfeatures.append(self.__extract_single_node(node, current_header))

        return optfeatures

    def __extract_single_node(self, optfeature_ast_node: Node, header: str) -> OptFeature:
        description, package_combinations = self.__extract_optfeature_command_arguments(optfeature_ast_node)
        visibility_conditions = self.__conditions_analyzer.analyze(optfeature_ast_node)
        return OptFeature(visibility_conditions, header, description, package_combinations)

    def __extract_optfeature_command_arguments(self, optfeature_command_node: Node) \
            -> Tuple[str, List[List[PackageWithUses]]]:
        description, *package_combinations = ast_node_utils.get_arguments_from_command_node(optfeature_command_node)

        package_combination_lists: List[List[PackageWithUses]] = []
        for package_combination in package_combinations:
            packages_with_uses: List[PackageWithUses] = []
            for package in package_combination.split(' '):
                package = self.__remove_variables_from_package_string(package)
                package = self.__remove_invalid_characters_from_package_string(package)
                packages_with_uses.append(self.__parse_package_with_uses(package))

            package_combination_lists.append(packages_with_uses)

        return description, package_combination_lists

    def __remove_invalid_characters_from_package_string(self, package_string: str) -> str:
        # Usually after removing a variable from the end of a package string, the last character will be ':'
        # so it should be removed
        if package_string.endswith(':'):
            return package_string[:-1]
        return package_string

    def __remove_variables_from_package_string(self, package_string: str) -> str:
        # This parser does not support variable expansion, so they are removed
        if '$' not in package_string:
            return package_string
        return package_string[:package_string.index('$')]

    def __parse_package_with_uses(self, package_string: str) -> PackageWithUses:
        # Package atoms can have USE flag requirements listed next to them within square brackets
        if '[' not in package_string:
            return PackageWithUses(package_string, None, None)

        start = package_string.index("[")
        end = package_string.index("]", start)

        package_name = package_string[:start]
        use_flags = package_string[start + 1:end].split(",")

        enabled_use_flags, disabled_use_flags = self.__determine_use_flag_categories(use_flags)

        return PackageWithUses(package_name, enabled_use_flags, disabled_use_flags)

    def __determine_use_flag_categories(self, use_flags: List[str]) -> Tuple[List[str], List[str]]:
        enabled_use_flags = []
        disabled_use_flags = []
        for use_flag in use_flags:
            if match := re.match(r"-(.+)", use_flag):
                disabled_use_flags.append(match.group(1))
            elif match := re.match(r"(.+)\(-\)", use_flag):
                disabled_use_flags.append(match.group(1))
            elif match := re.match(r"(.+)\(\+\)", use_flag):
                enabled_use_flags.append(match.group(1))
            else:
                enabled_use_flags.append(use_flag)

        return enabled_use_flags, disabled_use_flags
