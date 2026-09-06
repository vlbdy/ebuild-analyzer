import re

from ebuild_analyzer.arguments.config import Config
from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.ast.enums.command import Command
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.commands.handlers.command_handler import CommandHandler
from ebuild_analyzer.ebuild.ebuild import Ebuild
from ebuild_analyzer.optfeatures.optfeatures_extractor import OptFeaturesExtractor
from ebuild_analyzer.output.printers.optfeatures_printer import OptFeaturesPrinter
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.utils.portage_db import PortageDatabase


class OptFeaturesCommandHandler(CommandHandler):
    def __init__(self, config: Config, portage_db: PortageDatabase) -> None:
        self.__config = config
        self.__portage_db = portage_db

        self.__bash_parser = BashParser()
        self.__optfeatures_extractor = OptFeaturesExtractor()
        self.__optfeatures_printer = OptFeaturesPrinter(portage_db, config.show_ad_conditions,
                                                        config.run_unknown_commands)

    def handle(self, package_cpv: PackageCPV, ebuild: Ebuild) -> None:
        ebuild_ast = self.__bash_parser.parse(ebuild.contents)

        optfeature_ast_nodes = ebuild_ast.get_all_nodes_of_type(NodeType.COMMAND, re.compile(Command.OPTFEATURE))
        optfeatures = OptFeaturesExtractor().extract(optfeature_ast_nodes)

        if not optfeatures:
            if self.__config.verbose:
                print(f"Package '{package_cpv.text}' has no optional features")
        else:
            self.__optfeatures_printer.print(package_cpv, optfeatures)
