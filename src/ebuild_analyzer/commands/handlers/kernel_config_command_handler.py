from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.commands.handlers.command_handler import CommandHandler
from ebuild_analyzer.ebuild.ebuild import Ebuild
from ebuild_analyzer.kernel_config.kernel_config_keys_extractor import KernelConfigKeysExtractor
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV


class KernelConfigCommandHandler(CommandHandler):
    def __init__(self) -> None:
        self.__bash_parser = BashParser()
        self.__kernel_config_keys_extractor = KernelConfigKeysExtractor()

    def handle(self, package_cpv: PackageCPV, ebuild: Ebuild) -> None:
        ebuild_ast = self.__bash_parser.parse(ebuild.contents)

        # In Bash grammar, variable assignment nodes in the AST always start with the name of the variable
        # on the leftmost side. This means that I can reliably look for all variable assignment nodes that start
        # with the name of the variable I want.
        config_check_assignment_nodes = ebuild_ast.get_all_nodes_of_type(NodeType.VARIABLE_ASSIGNMENT, "CONFIG_CHECK")
        kernel_config_keys = self.__kernel_config_keys_extractor.extract(config_check_assignment_nodes)
        print(kernel_config_keys)
