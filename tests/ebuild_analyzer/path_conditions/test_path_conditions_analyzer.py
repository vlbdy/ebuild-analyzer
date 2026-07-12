from typing import List

import pytest
from tree_sitter import Node

from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.path_conditions.path_condition import PathCondition
from ebuild_analyzer.path_conditions.path_conditions_analyzer import PathConditionsAnalyzer


def __get_optfeature_command_node(bash_parser: BashParser, bash: bytes) -> Node:
    return bash_parser.parse(bash).get_all_nodes_of_type(NodeType.COMMAND, "optfeature")[0]


def test_no_conditions(bash_parser: BashParser, path_conditions_analyzer: PathConditionsAnalyzer):
    bash = b"optfeature"
    command_node = __get_optfeature_command_node(bash_parser, bash)

    assert path_conditions_analyzer.analyze(command_node) == []


@pytest.mark.parametrize("bash, expected_path_conditions", [
    (b"use a && optfeature", [PathCondition(enabled_use_flags=['a'])]),
    (b"use a || optfeature", [PathCondition(disabled_use_flags=['a'])]),

    (b"has_version pkg && optfeature", [PathCondition(installed_packages=[PackageAtom('pkg')])]),
    (b"has_version pkg || optfeature", [PathCondition(uninstalled_packages=[PackageAtom('pkg')])]),

    (b"use a && use b && optfeature", [PathCondition(enabled_use_flags=['a', 'b'])]),
    (b"use a || use b && optfeature", [PathCondition(enabled_use_flags=['a']), PathCondition(enabled_use_flags=['b'])]),
    (b"use a && use b || optfeature",
     [PathCondition(disabled_use_flags=['a']), PathCondition(disabled_use_flags=['b'])]),
    (b"use a || use b && optfeature", [PathCondition(enabled_use_flags=['a']), PathCondition(enabled_use_flags=['b'])]),
    (b"use a && use b || use c && optfeature",
     [PathCondition(enabled_use_flags=['a', 'b']), PathCondition(enabled_use_flags=['c'])]),

    (b"use a && has_version pkg && optfeature",
     [PathCondition(enabled_use_flags=['a'], installed_packages=[PackageAtom('pkg')])]),

    (b"use !a && optfeature", [PathCondition(disabled_use_flags=['a'])]),
    (b"! use a && optfeature", [PathCondition(disabled_use_flags=['a'])]),

    (b"use a && grep something /somewhere && optfeature",
     [PathCondition(enabled_use_flags=['a'], successful_commands=['grep something /somewhere'])]),
    (b"use a && ! grep something /somewhere && optfeature",
     [PathCondition(enabled_use_flags=['a'], failed_commands=['grep something /somewhere'])]),
    (b"use a || ! grep something /somewhere && optfeature",
     [PathCondition(enabled_use_flags=['a']), PathCondition(failed_commands=['grep something /somewhere'])]),
    (b"grep something /somewhere || optfeature",
     [PathCondition(failed_commands=['grep something /somewhere'])]),
])
def test_short_circuit_conditions(bash: bytes, expected_path_conditions: List[PathCondition], bash_parser: BashParser,
                                  path_conditions_analyzer: PathConditionsAnalyzer):
    command_node = __get_optfeature_command_node(bash_parser, bash)
    assert path_conditions_analyzer.analyze(command_node) == expected_path_conditions


@pytest.mark.parametrize("bash, expected_path_conditions", [
    (b"if use a; then optfeature; fi", [PathCondition(enabled_use_flags=['a'])]),
    (b"if has_version pkg; then optfeature; fi", [PathCondition(installed_packages=[PackageAtom('pkg')])]),

    (b"if some_command; then optfeature; fi", [PathCondition(successful_commands=['some_command'])]),
    (b"if ! some_command && some_command2; then optfeature; fi",
     [PathCondition(failed_commands=['some_command'], successful_commands=['some_command2'])]),

    (b"if use a && use b; then optfeature; fi", [PathCondition(enabled_use_flags=['a', 'b'])]),
    (b"if use a || use b; then optfeature; fi",
     [PathCondition(enabled_use_flags=['a']), PathCondition(enabled_use_flags=['b'])]),

    (b"if use a || ! use b; then optfeature; fi",
     [PathCondition(enabled_use_flags=['a']), PathCondition(disabled_use_flags=['b'])]),
    (b"if use !a && use b; then optfeature; fi", [PathCondition(disabled_use_flags=['a'], enabled_use_flags=['b'])]),

    (b"if use a; then if use b; then something; fi; optfeature; fi", [PathCondition(enabled_use_flags=['a'])]),
    (b"if use a; then optfeature; if use b; then something; fi; fi", [PathCondition(enabled_use_flags=['a'])]),
])
def test_if_statement_conditions(bash: bytes, expected_path_conditions: List[PathCondition], bash_parser: BashParser,
                                 path_conditions_analyzer: PathConditionsAnalyzer):
    command_node = __get_optfeature_command_node(bash_parser, bash)
    assert path_conditions_analyzer.analyze(command_node) == expected_path_conditions


@pytest.mark.parametrize("bash, expected_path_conditions", [
    (b"if use a; then if use b; then optfeature; fi; fi", [PathCondition(enabled_use_flags=['a', 'b'])]),
    (b"if use a; then if has_version pkg; then optfeature; fi; fi",
     [PathCondition(enabled_use_flags=['a'], installed_packages=[PackageAtom('pkg')])]),

    (b"if use a && use b; then if use c; then optfeature; fi; fi", [PathCondition(enabled_use_flags=['a', 'b', 'c'])]),
    (b"if use a; then if use b && use c; then optfeature; fi; fi", [PathCondition(enabled_use_flags=['a', 'b', 'c'])]),

    (b"if use a; then if use b || use c; then optfeature; fi; fi",
     [PathCondition(enabled_use_flags=['a', 'b']), PathCondition(enabled_use_flags=['a', 'c'])]),
    (b"if use a || use b; then if use c; then optfeature; fi; fi",
     [PathCondition(enabled_use_flags=['a', 'c']), PathCondition(enabled_use_flags=['b', 'c'])]),

    (b"if use a && use b; then if use c || use d; then optfeature; fi; fi",
     [PathCondition(enabled_use_flags=['a', 'b', 'c']), PathCondition(enabled_use_flags=['a', 'b', 'd'])]),
    (b"if use a || use b; then if use c && use d; then optfeature; fi; fi",
     [PathCondition(enabled_use_flags=['a', 'c', 'd']), PathCondition(enabled_use_flags=['b', 'c', 'd'])]),
    (b"if use a && use b; then if use c && use d; then optfeature; fi; fi",
     [PathCondition(enabled_use_flags=['a', 'b', 'c', 'd'])]),

    (b"if command a; then if command b && ! command c; then optfeature; fi; fi",
     [PathCondition(successful_commands=['command a', 'command b'], failed_commands=['command c'])])
])
def test_nested_if_statement_conditions(bash: bytes, expected_path_conditions: List[PathCondition],
                                        bash_parser: BashParser, path_conditions_analyzer: PathConditionsAnalyzer):
    command_node = __get_optfeature_command_node(bash_parser, bash)
    assert path_conditions_analyzer.analyze(command_node) == expected_path_conditions


@pytest.mark.parametrize("bash, expected_path_conditions", [
    (b"if use a; then use b && optfeature; fi", [PathCondition(enabled_use_flags=['a', 'b'])]),
    (b"if use a; then use b || optfeature; fi", [PathCondition(enabled_use_flags=['a'], disabled_use_flags=['b'])]),

    (b"if use a; then use b && use c && optfeature; fi", [PathCondition(enabled_use_flags=['a', 'b', 'c'])]),
    (b"if use a; then use b || use c && optfeature; fi",
     [PathCondition(enabled_use_flags=['a', 'b']), PathCondition(enabled_use_flags=['a', 'c'])]),

    (b"if some_command; then use b && use c && optfeature; fi",
     [PathCondition(successful_commands=['some_command'], enabled_use_flags=['b', 'c'])]),
])
def test_if_conditions_mixed_with_short_circuit_conditions(bash: bytes, expected_path_conditions: List[PathCondition],
                                                           bash_parser: BashParser,
                                                           path_conditions_analyzer: PathConditionsAnalyzer):
    command_node = __get_optfeature_command_node(bash_parser, bash)
    assert path_conditions_analyzer.analyze(command_node) == expected_path_conditions


@pytest.mark.xfail(reason="Not implemented")
@pytest.mark.parametrize("bash, expected_path_conditions", [
    (b"use a && optfeature && use b", [PathCondition(enabled_use_flags=['a'])]),

    # The following test cases are similar to the test cases in `test_nested_if_statement_conditions`.
    # The difference is that those tests are technically also supposed to have the extra PathCondition added
    # to the end (where all the conditions in the OR'd commands are met).
    (b"use a && use b && use c || use d && optfeature",
     [PathCondition(enabled_use_flags=['a', 'c']), PathCondition(enabled_use_flags=['b', 'c']),
      PathCondition(enabled_use_flags=['a', 'b', 'c'])]),

    (b"if use a; then if use b || use c; then optfeature; fi; fi",
     [PathCondition(enabled_use_flags=['a', 'b']), PathCondition(enabled_use_flags=['a', 'c']),
      PathCondition(enabled_use_flags=['a', 'b', 'c'])]),
    (b"if use a || use b; then if use c; then optfeature; fi; fi",
     [PathCondition(enabled_use_flags=['a', 'c']), PathCondition(enabled_use_flags=['b', 'c']),
      PathCondition(enabled_use_flags=['a', 'b', 'c'])]),

    (b"if use a && use b; then if use c || use d; then optfeature; fi; fi",
     [PathCondition(enabled_use_flags=['a', 'b', 'c']), PathCondition(enabled_use_flags=['a', 'b', 'd']),
      PathCondition(enabled_use_flags=['a', 'b', 'c', 'd'])]),
    (b"if use a || use b; then if use c && use d; then optfeature; fi; fi",
     [PathCondition(enabled_use_flags=['a', 'c', 'd']), PathCondition(enabled_use_flags=['b', 'c', 'd']),
      PathCondition(enabled_use_flags=['a', 'b', 'c', 'd'])]),

    (b"if use a || use b; then if use c || use d; then optfeature; fi; fi",
     [PathCondition(enabled_use_flags=['a', 'c']), PathCondition(enabled_use_flags=['a', 'd']),
      PathCondition(enabled_use_flags=['b', 'c']), PathCondition(enabled_use_flags=['b', 'd']),
      PathCondition(enabled_use_flags=['a', 'b', 'c']), PathCondition(enabled_use_flags=['a', 'b', 'd']),
      PathCondition(enabled_use_flags=['a', 'c', 'd']), PathCondition(enabled_use_flags=['b', 'c', 'd']),
      PathCondition(enabled_use_flags=['a', 'b', 'c', 'd'])])
])
def test_unimplemented_cases(bash: bytes, expected_path_conditions: List[PathCondition], bash_parser: BashParser,
                             path_conditions_analyzer: PathConditionsAnalyzer):
    command_node = __get_optfeature_command_node(bash_parser, bash)
    assert path_conditions_analyzer.analyze(command_node) == expected_path_conditions
