from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.commands.handlers.command_handler import CommandHandler
from ebuild_analyzer.ebuild.ebuild import Ebuild
from ebuild_analyzer.kernel_config.checked.checked_kernel_config_extractor import CheckedKernelConfigExtractor
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV


class KernelConfigCommandHandler(CommandHandler):
    def __init__(self) -> None:
        self.__bash_parser = BashParser()
        self.__kernel_config_keys_extractor = CheckedKernelConfigExtractor()

    def handle(self, package_cpv: PackageCPV, ebuild: Ebuild) -> None:
        ebuild_ast = self.__bash_parser.parse(ebuild.contents)
        kernel_config_keys = self.__kernel_config_keys_extractor.extract(ebuild_ast)
        print(kernel_config_keys)
