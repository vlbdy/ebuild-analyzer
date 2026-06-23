import re

import tree_sitter_bash
from tree_sitter import Parser, Language

from parser.ebuild_ast import EbuildAST


class Ebuild:
    def __init__(self, path: str) -> None:
        self.__path = path

    def get_normalized_contents(self) -> bytes:
        with open(self.__path, "rb") as ebuild_file:
            ebuild_contents = ebuild_file.read()
            # Join lines that use backslash line continuation
            ebuild_contents = re.sub(rb'\\\n\s*', b'', ebuild_contents)
            return ebuild_contents

    def parse_to_ast(self) -> EbuildAST:
        parser = Parser()
        parser.language = Language(tree_sitter_bash.language())
        return EbuildAST(parser.parse(self.get_normalized_contents()))
