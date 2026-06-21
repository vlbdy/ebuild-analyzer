import sys

from output import optfeatures_printer
from output.ansi import Format, Color
from parser import optfeature_parser
from parser.ebuild_ast import EbuildAST
from utils import package_utils, ebuild_utils

"""
After parsing the bash script with tree sitter, iterate over all the optfeature commands and then go up the tree
recording every conditional statement (if, &&, ||, use, has_version) until the root is reached
"""


def usage():
    print(f"""\
Usage: {sys.argv[0]} <COMMAND> <PACKAGE>

Available commands:
    {Format.BOLD("optfeatures")} - Prints the available optional features of the package\
""")


def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    command = sys.argv[1]
    package = sys.argv[2]

    if command == "optfeatures":
        ebuild_path = package_utils.get_ebuild_path_for_installed_package(package)
        print(Format.BOLD("Found ebuild at: ") + Color.GREEN(ebuild_path))

        ebuild_contents = ebuild_utils.get_normalized_ebuild_contents(ebuild_path)

        tree = ebuild_utils.parse_to_ast(ebuild_contents)

        optfeature_ast_nodes = EbuildAST(tree).get_all_optfeature_nodes()

        optfeatures = optfeature_parser.parse_multiple_optfeature_nodes(optfeature_ast_nodes)

        optfeatures_printer.print_optfeatures(package, optfeatures)
    else:
        print(Color.RED(f"Unknown command '{command}'"))
        usage()


if __name__ == "__main__":
    main()
