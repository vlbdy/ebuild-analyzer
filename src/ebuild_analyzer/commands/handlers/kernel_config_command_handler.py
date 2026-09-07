from ebuild_analyzer.arguments.config import Config
from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.commands.handlers.command_handler import CommandHandler
from ebuild_analyzer.ebuild.ebuild import Ebuild
from ebuild_analyzer.kernel_config.checked.checked_kernel_config_extractor import CheckedKernelConfigExtractor
from ebuild_analyzer.kernel_config.local.local_kernel_config_factory import LocalKernelConfigFactory
from ebuild_analyzer.output.printers.checked_kernel_config_printer import CheckedKernelConfigPrinter
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.utils.portage_db import PortageDatabase


class KernelConfigCommandHandler(CommandHandler):
    def __init__(self, config: Config, portage_db: PortageDatabase) -> None:
        self.__config = config

        self.__bash_parser = BashParser()
        self.__kernel_config_keys_extractor = CheckedKernelConfigExtractor()

        if self.__config.kernel_config:
            kernel_config = LocalKernelConfigFactory().from_file(self.__config.kernel_config)
        else:
            kernel_config = LocalKernelConfigFactory().from_running_kernel()
        self.__checked_kernel_config_printer = CheckedKernelConfigPrinter(portage_db, config, kernel_config)

    def handle(self, package_cpv: PackageCPV, ebuild: Ebuild) -> None:
        ebuild_ast = self.__bash_parser.parse(ebuild.contents)
        kernel_config_keys = self.__kernel_config_keys_extractor.extract(ebuild_ast)

        if kernel_config_keys:
            self.__checked_kernel_config_printer.print(package_cpv, kernel_config_keys)
        elif self.__config.verbose:
            print(f"Package '{package_cpv.text}' has no checked kernel configuration")
