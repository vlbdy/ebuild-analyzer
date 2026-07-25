from typing import List

from ebuild_analyzer.package_atoms.package_atom_parser import PackageAtomParser
from ebuild_analyzer.path_conditions.command_interpreters.command_interpreter import CommandInterpreter
from ebuild_analyzer.path_conditions.path_condition import PathCondition


class HasVersionCommandInterpreter(CommandInterpreter):
    def __init__(self):
        self.__package_atom_parser = PackageAtomParser()

    def create_path_conditions(self, arguments: List[str]) -> PathCondition:
        return PathCondition(installed_packages={self.__package_atom_parser.parse(arguments[0])})
