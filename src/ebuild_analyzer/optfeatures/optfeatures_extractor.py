from typing import List

from tree_sitter import Node

from ebuild_analyzer.ast import ast_node_utils
from ebuild_analyzer.ast.enums.command import Command
from ebuild_analyzer.optfeatures.optfeature import OptFeature
from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.package_atoms.package_atom_parser import PackageAtomParser
from ebuild_analyzer.path_conditions.path_conditions_analyzer import PathConditionsAnalyzer


class OptFeaturesExtractor:
    def __init__(self) -> None:
        self.__conditions_analyzer = PathConditionsAnalyzer()
        self.__package_atom_parser = PackageAtomParser()

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

    def __extract_single_node(self, optfeature_command_node: Node, header: str) -> OptFeature:
        optfeature_arguments = ast_node_utils.get_arguments_from_command_node(optfeature_command_node)

        description = optfeature_arguments[0]
        package_combinations = self.__extract_feature_dependencies(optfeature_arguments[1:])
        visibility_conditions = self.__conditions_analyzer.analyze(optfeature_command_node)
        return OptFeature(visibility_conditions, header, description, package_combinations)

    def __extract_feature_dependencies(self, package_combinations: List[str]) -> List[List[PackageAtom]]:
        package_combination_lists: List[List[PackageAtom]] = []
        for package_combination in package_combinations:
            package_atoms: List[PackageAtom] = []

            for package_string in package_combination.split(' '):
                package_string = self.__remove_variables_from_package_string(package_string)
                package_string = self.__remove_invalid_characters_from_package_string(package_string)
                package_atoms.append(self.__package_atom_parser.parse(package_string))

            package_combination_lists.append(package_atoms)

        return package_combination_lists

    def __remove_invalid_characters_from_package_string(self, package_string: str) -> str:
        # Usually after removing a variable from the end of a package string, the last character will be ':'
        # so it should be removed
        if package_string.endswith(':'):
            return package_string[:-1]
        return package_string

    def __remove_variables_from_package_string(self, package_string: str) -> str:
        # This parser does not fully support variable expansion, so unexpanded variables are removed to ensure
        # that the ebuild analyzer can still work.
        if '$' not in package_string:
            return package_string
        return package_string[:package_string.index('$')]
