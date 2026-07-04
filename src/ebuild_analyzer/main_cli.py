import sys

from portage.exception import InvalidAtom

from ebuild_analyzer import arguments_parser
from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.ast.enums.command import Command
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.debug import dump_ast
from ebuild_analyzer.optfeatures.optfeatures_extractor import OptFeaturesExtractor
from ebuild_analyzer.output.ansi import Format, Color
from ebuild_analyzer.output.printers.optfeatures_printer import OptFeaturesPrinter
from ebuild_analyzer.package_atoms.package_atom_parser import PackageAtomParser
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.utils.ebuild import Ebuild
from ebuild_analyzer.utils.portage_db import PortageDatabase, AmbiguousPackageException, PackageNotFoundException

args = arguments_parser.create().parse_args()


def dump_ast_for_package(portage_db: PortageDatabase, package_cpv: PackageCPV) -> None:
    ebuild_path = portage_db.get_ebuild_path_for_package(package_cpv)
    ebuild = Ebuild(package_cpv, portage_db, ebuild_path)
    ebuild_ast = BashParser().parse(ebuild.get_normalized_contents())
    dump_ast(ebuild_ast.get_tree().root_node, ebuild.get_normalized_contents())


def print_optfeatures_for_package(portage_db: PortageDatabase, package_cpv: PackageCPV, show_ad_conditions: bool) -> None:
    ebuild_path = portage_db.get_ebuild_path_for_package(package_cpv)
    if args.verbose:
        print(Format.BOLD("Found ebuild at: ") + Color.GREEN(ebuild_path))

    ebuild = Ebuild(package_cpv, portage_db, ebuild_path)
    ebuild_ast = BashParser().parse(ebuild.get_normalized_contents())

    optfeature_ast_nodes = ebuild_ast.get_all_nodes_of_type(NodeType.COMMAND, Command.OPTFEATURE)
    optfeatures = OptFeaturesExtractor().extract(optfeature_ast_nodes)

    if not optfeatures:
        if args.verbose:
            print(f"Package '{package_cpv.text}' has no optional features")
        return
    package_atom = PackageAtomParser().parse(package_cpv.text)
    OptFeaturesPrinter(portage_db, show_ad_conditions).print(package_atom, optfeatures)


def main():
    command = args.command
    package = args.package

    if not package and not args.all:
        print(Color.RED("error: PACKAGE is required unless --all is specified"))
        sys.exit(1)

    portage_db = PortageDatabase()
    package_atom_parser = PackageAtomParser()

    try:
        if command == "optfeatures":
            show_ad_conditions = args.show_ad_conditions
            if args.all:
                for package in portage_db.get_all_packages():
                    print_optfeatures_for_package(portage_db, package, show_ad_conditions)
            else:
                package_atom = package_atom_parser.parse(package)
                print_optfeatures_for_package(portage_db, portage_db.get_cpv_for_atom(package_atom), show_ad_conditions)
        elif command == "dump-ast":
            package_atom = package_atom_parser.parse(package)
            dump_ast_for_package(portage_db, portage_db.get_cpv_for_atom(package_atom))
    except (AmbiguousPackageException, PackageNotFoundException) as e:
        print(Color.RED(str(e)))
    except InvalidAtom as e:
        print(Color.RED(f"Invalid package atom: '{e}'"))


if __name__ == "__main__":
    main()
