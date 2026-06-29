from ebuild_analyzer.ast.enums.node_types import NodeType


class NoMatchingChildNodeException(Exception):
    def __init__(self, node_type: NodeType):
        super().__init__(f"No matching child node of type {node_type.value} found")
