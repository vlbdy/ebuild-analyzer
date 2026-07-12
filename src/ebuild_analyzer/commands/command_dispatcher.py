from typing import List, Dict, Optional

from portage.exception import InvalidAtom, AmbiguousPackageName

from ebuild_analyzer.arguments.config import Config
from ebuild_analyzer.commands.handlers.command_handler import CommandHandler
from ebuild_analyzer.commands.handlers.dump_ast_command_handler import DumpAstCommandHandler
from ebuild_analyzer.commands.handlers.optfeatures_command_handler import OptFeaturesCommandHandler
from ebuild_analyzer.ebuild.ebuild import Ebuild
from ebuild_analyzer.ebuild.ebuild_preprocessor import EbuildPreprocessor
from ebuild_analyzer.ebuild.ebuild_variables_resolver import EbuildVariablesResolver
from ebuild_analyzer.output.ansi import Color, Format
from ebuild_analyzer.package_atoms.package_atom_parser import PackageAtomParser
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.utils.portage_db import PortageDatabase, PackageNotFoundException


class CommandDispatcher:
    def __init__(self, config: Config) -> None:
        self.__config = config
        self.__portage_db = PortageDatabase()
        self.__package_atom_parser = PackageAtomParser()
        self.__ebuild_preprocessor = EbuildPreprocessor(EbuildVariablesResolver(self.__portage_db))

        self.__command_handlers: Dict[str, CommandHandler] = {
            "optfeatures": OptFeaturesCommandHandler(config, self.__portage_db),
            "dump-ast": DumpAstCommandHandler(),
        }

    def dispatch(self) -> None:
        try:
            self.__dispatch_command()
        except (PackageNotFoundException, InvalidAtom, AmbiguousPackageName) as e:
            self.__report_exception(e)

    def __dispatch_command(self) -> None:
        for cpv in self.__get_package_cpvs():
            self.__process_cpv(cpv)

    def __process_cpv(self, cpv: PackageCPV) -> None:
        try:
            ebuild = self.__get_ebuild(cpv)
            self.__command_handlers[self.__config.command].handle(cpv, ebuild)
        except (PackageNotFoundException, InvalidAtom, AmbiguousPackageName) as e:
            self.__report_exception(e, cpv)

    def __get_ebuild(self, package_cpv: PackageCPV) -> Ebuild:
        ebuild = self.__portage_db.get_ebuild(package_cpv)
        if self.__config.verbose:
            print(Format.BOLD("Found ebuild at: ") + Color.GREEN(ebuild.path))

        return self.__ebuild_preprocessor.preprocess(ebuild)

    def __get_package_cpvs(self) -> List[PackageCPV]:
        if self.__config.all:
            return self.__portage_db.get_all_installed_packages()
        else:
            return [self.__portage_db.get_best_visible_cpv(self.__package_atom_parser.parse(self.__config.package))]

    def __report_exception(self, exception: Exception, cpv: Optional[PackageCPV] = None) -> None:
        if cpv is not None:
            print(Color.RED(f"Failed to process the following package: {cpv.text}"))

        match exception:
            case PackageNotFoundException() as e:
                print(Color.RED("error: ") + str(e))
            case InvalidAtom() as e:
                print(Color.RED("error: ") + f"Invalid package atom: '{e}'")
            case AmbiguousPackageName() as e:
                print(Color.RED("error: ") + f"Ambiguous package name '{self.__config.package}'. Candidates are {e}.")
