from typing import List

from ebuild_analyzer.ast.enums.node_types import NodeType


class UnexpectedNodeTypeException(Exception):
    # The `passed_node_type` is the raw tree sitter type
    def __init__(self, expected_node_types: List[NodeType], passed_node_type: str):
        super().__init__(f"Unexpected node type {passed_node_type} when expected one of "
                         f"{[node_type.value for node_type in expected_node_types]}")
