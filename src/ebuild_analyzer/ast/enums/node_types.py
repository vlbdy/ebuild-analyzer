from enum import StrEnum


class NodeType(StrEnum):
    COMMAND = "command"
    NEGATED_COMMAND = "negated_command"
    COMMAND_NAME = "command_name"
    STRING = "string"
    RAW_STRING = "raw_string"
    LIST = "list"
    IF_STATEMENT = "if_statement"
    THEN = "then"
    PROGRAM = "program"
    OR = "||"
    AND = "&&"
    VARIABLE_ASSIGNMENT = "variable_assignment"
    ELSE_CLAUSE = "else_clause"
    ELIF_CLAUSE = "elif_clause"
