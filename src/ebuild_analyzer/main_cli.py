import argparse
import sys

from portage.exception import InvalidAtom

from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.ast.enums.command import Command
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.debug import dump_ast
from ebuild_analyzer.extractor.optfeatures_extractor import OptFeaturesExtractor
from ebuild_analyzer.output.ansi import Format, Color
from ebuild_analyzer.output.optfeatures_printer import OptFeaturesPrinter
from ebuild_analyzer.utils.ebuild import Ebuild
from ebuild_analyzer.utils.portage_db import PortageDatabase, AmbiguousPackageException, PackageNotFoundException

parser = argparse.ArgumentParser(prog="ebuild-analyzer")

parser.add_argument(
    "--all", "-a",
    action="store_true",
    help="Query all installed packages",
    default=False,
)
parser.add_argument(
    "--verbose", "-v",
    action="store_true",
    help="Verbose messages",
    default=False,
)

subparsers = parser.add_subparsers(
    dest="command",
    required=True,
)

optfeatures_parser = subparsers.add_parser(
    "optfeatures",
    help="Extract optfeatures",
)
optfeatures_parser.add_argument("package", nargs="?")

kernel_parser = subparsers.add_parser(
    "kernel-config",
    help="Extract kernel config requirements",
)
kernel_parser.add_argument("package", nargs="?")

dump_ast_parser = subparsers.add_parser(
    "dump-ast",
    help="Dump tree sitter AST for the ebuild (for debugging)"
)
dump_ast_parser.add_argument("package")

args = parser.parse_args()


def dump_ast_for_package(portage_db: PortageDatabase, package: str) -> None:
    ebuild_path = portage_db.get_ebuild_path_for_package(package)
    ebuild = Ebuild(package, portage_db, ebuild_path)
    ebuild_ast = BashParser().parse(ebuild.get_normalized_contents())
    dump_ast(ebuild_ast.get_tree().root_node, ebuild.get_normalized_contents())


def print_optfeatures_for_package(portage_db: PortageDatabase, package: str) -> None:
    ebuild_path = portage_db.get_ebuild_path_for_package(package)
    if args.verbose:
        print(Format.BOLD("Found ebuild at: ") + Color.GREEN(ebuild_path))

    ebuild = Ebuild(package, portage_db, ebuild_path)
    ebuild_ast = BashParser().parse(ebuild.get_normalized_contents())

    optfeature_ast_nodes = ebuild_ast.get_all_nodes_of_type(NodeType.COMMAND, Command.OPTFEATURE)
    optfeatures = OptFeaturesExtractor().extract(optfeature_ast_nodes)

    if not optfeatures:
        if args.verbose:
            print(f"Package '{package}' has no optional features")
        return
    OptFeaturesPrinter(portage_db).print_optfeatures(package, optfeatures)


def main():
    command = args.command
    package = args.package

    if not package and not args.all:
        print(Color.RED("error: PACKAGE is required unless --all is specified"))
        sys.exit(1)

    portage_db = PortageDatabase()

    try:
        if command == "optfeatures":
            if args.all:
                for package in portage_db.get_all_packages():
                    print_optfeatures_for_package(portage_db, package)
            else:
                print_optfeatures_for_package(portage_db, package)
        elif command == "dump-ast":
            dump_ast_for_package(portage_db, package)
    except (AmbiguousPackageException, PackageNotFoundException) as e:
        print(Color.RED(str(e)))
    except InvalidAtom as e:
        print(Color.RED(f"Invalid package atom: '{e}'"))


if __name__ == "__main__":
    main()
