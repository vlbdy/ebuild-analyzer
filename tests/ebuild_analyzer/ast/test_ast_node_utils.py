import re
from typing import List, Callable

import pytest

from ebuild_analyzer.ast import ast_node_utils
from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.ast.exceptions.no_matching_child_node_exception import NoMatchingChildNodeException
from ebuild_analyzer.ast.exceptions.unexpected_node_type_exception import UnexpectedNodeTypeException


class TestFindClosestChildNodeOfType:
    BASH = b"""
    my_func() {
        if something; then
            my_command
        fi
    }
    """

    def test_sanity(self, bash_parser: BashParser):
        ast = bash_parser.parse(self.BASH)

        if_statement_node = ast.get_all_nodes_of_type(NodeType.IF_STATEMENT)[0]
        node = ast_node_utils.find_closest_direct_child_node_of_type(NodeType.COMMAND, if_statement_node)

        assert node.type == NodeType.COMMAND
        assert node.text == b"something"

    def test_raises_on_node_type_that_doesnt_exist_in_any_child(self, bash_parser: BashParser):
        ast = bash_parser.parse(self.BASH)
        root_node = ast.get_tree().root_node

        with pytest.raises(NoMatchingChildNodeException):
            ast_node_utils.find_closest_direct_child_node_of_type(NodeType.AND, root_node)


def test_get_command_name_from_command_node_sanity(bash_parser: BashParser):
    test_command_name = "my_test_command"
    bash = f"{test_command_name} arg1 arg2".encode()
    ast = bash_parser.parse(bash)
    command_node = ast_node_utils.find_closest_direct_child_node_of_type(NodeType.COMMAND, ast.get_tree().root_node)

    assert ast_node_utils.get_command_name_from_command_node(command_node) == test_command_name


@pytest.mark.parametrize("arguments, expected_output_arguments", [
    ("arg1", ['arg1']),
    ("arg1 arg2 'arg3 arg4' arg5", ['arg1', 'arg2', 'arg3 arg4', 'arg5']),
    ("", []),
])
def test_get_arguments_from_command_node_sanity(bash_parser: BashParser, arguments: str,
                                                expected_output_arguments: List[str]):
    bash = f"command {arguments}".encode()
    ast = bash_parser.parse(bash)
    command_node = ast_node_utils.find_closest_direct_child_node_of_type(NodeType.COMMAND, ast.get_tree().root_node)

    assert ast_node_utils.get_arguments_from_command_node(command_node) == expected_output_arguments


def test_get_all_condition_nodes_sanity(bash_parser: BashParser):
    bash = b"""
    if a && b || c; then 
        my_command
    fi
    """
    ast = bash_parser.parse(bash)
    if_statement_node = ast_node_utils.find_closest_direct_child_node_of_type(NodeType.IF_STATEMENT, ast.get_tree().root_node)

    condition_nodes = ast_node_utils.get_all_condition_nodes(if_statement_node)

    # The first condition node is always an 'if' node
    assert condition_nodes[1].type == NodeType.LIST and condition_nodes[1].text == b"a && b || c"
    assert len(condition_nodes) == 3  # 'if', 'list', ';'
    for node in condition_nodes:
        assert node.type != NodeType.COMMAND
        assert node.text != b"my_command"


@pytest.mark.parametrize("func", [
    ast_node_utils.get_command_name_from_command_node,
    ast_node_utils.get_arguments_from_command_node,
    ast_node_utils.get_all_condition_nodes,
])
def test_raise_unexpected_node_type_exception(bash_parser: BashParser, func: Callable):
    bash = b"my_func(){}"
    ast = bash_parser.parse(bash)
    root_node = ast.get_tree().root_node

    with pytest.raises(UnexpectedNodeTypeException):
        ast_node_utils.get_all_condition_nodes(root_node)


def test_is_descendant(bash_parser: BashParser):
    bash = b"a && b || c && d"
    ast = bash_parser.parse(bash)

    # Bash grammar parses this into the following structure (excluding the operators && and ||):
    # list_abcd
    # ├── list_abc
    # │   ├── list_ab
    # │   │   ├── a
    # │   │   └── b
    # │   └── c
    # └── d
    list_abcd, list_abc, list_ab = ast.get_all_nodes_of_type(NodeType.LIST)
    a = ast.get_all_nodes_of_type(NodeType.COMMAND, re.compile("a"))[0]
    b = ast.get_all_nodes_of_type(NodeType.COMMAND, re.compile("b"))[0]
    c = ast.get_all_nodes_of_type(NodeType.COMMAND, re.compile("c"))[0]
    d = ast.get_all_nodes_of_type(NodeType.COMMAND, re.compile("d"))[0]

    assert ast_node_utils.is_descendant(list_abcd, list_abc)
    assert ast_node_utils.is_descendant(list_abcd, list_ab)
    assert ast_node_utils.is_descendant(list_abcd, a)
    assert ast_node_utils.is_descendant(list_abcd, b)
    assert ast_node_utils.is_descendant(list_abcd, c)
    assert ast_node_utils.is_descendant(list_abcd, d)

    assert ast_node_utils.is_descendant(list_abc, list_ab)
    assert ast_node_utils.is_descendant(list_abc, a)
    assert ast_node_utils.is_descendant(list_abc, b)
    assert ast_node_utils.is_descendant(list_abc, c)

    assert ast_node_utils.is_descendant(list_ab, a)
    assert ast_node_utils.is_descendant(list_ab, b)

    assert not ast_node_utils.is_descendant(list_abc, list_abcd)
    assert not ast_node_utils.is_descendant(list_abc, d)

    assert not ast_node_utils.is_descendant(list_ab, list_abc)
    assert not ast_node_utils.is_descendant(list_ab, list_abcd)
    assert not ast_node_utils.is_descendant(list_ab, c)
    assert not ast_node_utils.is_descendant(list_ab, d)

    assert not ast_node_utils.is_descendant(c, a)
    assert not ast_node_utils.is_descendant(c, b)
