from typing import List, Any

from tree_sitter import Node

from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.ast.exceptions.no_matching_child_node_exception import NoMatchingChildNodeException
from ebuild_analyzer.ast.exceptions.unexpected_node_type_exception import UnexpectedNodeTypeException


def find_closest_direct_child_node_of_type(node_type: NodeType, node: Node) -> Node:
    for child in node.children:
        if child.type == node_type:
            return child
    raise NoMatchingChildNodeException(node_type)


def get_command_name_from_command_node(command_node: Node) -> str:
    if command_node.type != NodeType.COMMAND:
        raise UnexpectedNodeTypeException([NodeType.COMMAND], command_node.type)
    return find_closest_direct_child_node_of_type(NodeType.COMMAND_NAME, command_node).text.decode()


def get_arguments_from_command_node(command_node: Node) -> List[str]:
    if command_node.type != NodeType.COMMAND:
        raise UnexpectedNodeTypeException([NodeType.COMMAND], command_node.type)

    arguments = []
    for child in command_node.children:
        if child.type == NodeType.COMMAND_NAME:
            continue
        if child.type == NodeType.STRING or child.type == NodeType.RAW_STRING:
            # Remove the " or ' at the start and the end
            arguments.append(child.text.decode()[1:-1])
        else:
            arguments.append(child.text.decode())
    return arguments


def get_all_condition_nodes(conditional_node: Node) -> List[Node]:
    if conditional_node.type not in (NodeType.IF_STATEMENT, NodeType.ELIF_CLAUSE):
        raise UnexpectedNodeTypeException([NodeType.IF_STATEMENT, NodeType.ELIF_CLAUSE], conditional_node.type)

    condition_nodes: List[Node] = []
    for child in conditional_node.children:
        # End of condition nodes
        if child.type == NodeType.THEN:
            break
        condition_nodes.append(child)

    return condition_nodes


def get_value_of_variable_assignment_node(variable_assignment_node: Node) -> Any:
    if variable_assignment_node.type != NodeType.VARIABLE_ASSIGNMENT:
        raise UnexpectedNodeTypeException([NodeType.VARIABLE_ASSIGNMENT], variable_assignment_node.type)

    # Most variable assignments are of the form
    # <variable> <operator> <value>
    #  index 0    index 1   index 2
    value_node = variable_assignment_node.children[-1]
    # Empty value
    if value_node.text == b'=':
        return ""

    if value_node.type in (NodeType.STRING, NodeType.RAW_STRING):
        return value_node.text.decode()[1:-1]  # Remove the ' or " from the ends of the string
    else:
        return value_node.text.decode()


def get_variable_name_from_variable_assignment_node(variable_assignment_node: Node) -> str:
    if variable_assignment_node.type != NodeType.VARIABLE_ASSIGNMENT:
        raise UnexpectedNodeTypeException([NodeType.VARIABLE_ASSIGNMENT], variable_assignment_node.type)

    # Most variable assignments are of the form
    # <variable> <operator> <value>
    #  index 0    index 1   index 2
    value_node = variable_assignment_node.children[0]
    return value_node.text.decode()


def is_command_node(node: Node) -> bool:
    return node.type in (NodeType.COMMAND, NodeType.NEGATED_COMMAND)


def is_compound_node(node: Node) -> bool:
    return node.type in (NodeType.IF_STATEMENT, NodeType.LIST, NodeType.ELIF_CLAUSE)


def is_descendant(ancestor: Node, node: Node) -> bool:
    for child in ancestor.children:
        if child == node or is_descendant(child, node):
            return True
    return False
