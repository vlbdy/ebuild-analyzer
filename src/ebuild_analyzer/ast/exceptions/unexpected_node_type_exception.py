from ebuild_analyzer.ast.enums.node_types import NodeType


class UnexpectedNodeTypeException(Exception):
    # The `passed_node_type` is the raw tree sitter type
    def __init__(self, expected_node_type: NodeType, passed_node_type: str):
        super().__init__(f"Unexpected node type {passed_node_type} when expected {expected_node_type.value}")
