import re

import tree_sitter_bash
from tree_sitter import Tree, Parser, Language


def get_normalized_ebuild_contents(ebuild_path: str) -> bytes:
    with open(ebuild_path, "rb") as ebuild_file:
        ebuild_contents = ebuild_file.read()
        # Join lines that use backslash line continuation
        ebuild_contents = re.sub(rb'\\\n\s*', b'', ebuild_contents)
        return ebuild_contents


def parse_to_ast(ebuild_contents: bytes) -> Tree:
    parser = Parser()
    parser.language = Language(tree_sitter_bash.language())
    return parser.parse(ebuild_contents)
