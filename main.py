import argparse

from output import optfeatures_printer
from output.ansi import Format, Color
from parser import optfeature_parser
from parser.ebuild_ast import EbuildAST
from utils import package_utils, ebuild_utils

parser = argparse.ArgumentParser(prog="ebuild-analyzer")

parser.add_argument(
    "--all",
    action="store_true",
    help="Query all installed packages",
)

subparsers = parser.add_subparsers(
    dest="command",
    required=True,
)

optfeatures_parser = subparsers.add_parser(
    "optfeatures",
    help="Extract optfeatures",
)
optfeatures_parser.add_argument("package")

kernel_parser = subparsers.add_parser(
    "kernel-config",
    help="Extract kernel config requirements",
)
kernel_parser.add_argument("package")


def main():
    args = parser.parse_args()
    command = args.command
    package = args.package

    if command == "optfeatures":
        ebuild_path = package_utils.get_ebuild_path_for_installed_package(package)
        print(Format.BOLD("Found ebuild at: ") + Color.GREEN(ebuild_path))

        ebuild_contents = ebuild_utils.get_normalized_ebuild_contents(ebuild_path)

        tree = ebuild_utils.parse_to_ast(ebuild_contents)

        optfeature_ast_nodes = EbuildAST(tree).get_all_optfeature_nodes()

        optfeatures = optfeature_parser.parse_multiple_optfeature_nodes(optfeature_ast_nodes)

        optfeatures_printer.print_optfeatures(package, optfeatures)


if __name__ == "__main__":
    main()
