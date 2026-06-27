import tree_sitter_bash
from tree_sitter import Parser, Language

from ebuild_analyzer.ast.bash_ast import BashAST


class BashParser:
    def __init__(self):
        self.__parser = Parser()
        self.__parser.language = Language(tree_sitter_bash.language())

    def parse(self, data: bytes) -> BashAST:
        return BashAST(self.__parser.parse(data))
