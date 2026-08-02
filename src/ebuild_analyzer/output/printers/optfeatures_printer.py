from collections import defaultdict
from typing import List

from ebuild_analyzer.optfeatures.optfeature import OptFeature
from ebuild_analyzer.optfeatures.optfeature_availability_checker import OptFeatureAvailabilityChecker
from ebuild_analyzer.output.ansi import Format, Color
from ebuild_analyzer.output.printers.base_printer import BasePrinter
from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.path_conditions.path_condition import PathCondition
from ebuild_analyzer.utils.portage_db import PortageDatabase


class OptFeaturesPrinter(BasePrinter):
    def __init__(self, portage_db: PortageDatabase, show_ad_conditions: bool, run_unknown_commands: bool) -> None:
        super().__init__(portage_db, run_unknown_commands)

        self.__show_ad_conditions = show_ad_conditions
        self.__optfeature_availability_checker = OptFeatureAvailabilityChecker(portage_db)

    def print(self, package_cpv: PackageCPV, optfeatures: List[OptFeature]) -> None:
        self._buffer.reset()
        self._buffer.push(Color.LIGHT_PURPLE(Format.BOLD(f"Optional features for package {package_cpv.text}:\n")))
        self._buffer.push_indent()

        optfeatures_groups = defaultdict(list)
        for optfeature in optfeatures:
            optfeatures_groups[optfeature.header].append(optfeature)

        for header, optfeatures in optfeatures_groups.items():
            if header is not None:
                self._buffer.indented_push(Color.BLUE(Format.BOLD(f"{header}\n")))
                self._buffer.push_indent()

            for optfeature in optfeatures:
                self._buffer.indented_push(Format.BOLD(optfeature.description))
                self.__print_feature_availability(optfeature)

                if optfeature.visibility_conditions and self.__show_ad_conditions:
                    self.__print_optfeature_visibility_conditions(package_cpv, optfeature.visibility_conditions)
                self.__print_packages_required_to_enable_optfeature(optfeature.possible_feature_dependencies)
                self._buffer.push('\n')
            self._buffer.pop_indent()
        self._buffer.print()

    def __print_feature_availability(self, optfeature: OptFeature) -> None:
        is_feature_available = self.__optfeature_availability_checker.is_available(optfeature)

        self._buffer.push(Color.BLUE(" ["))
        if is_feature_available:
            self._buffer.push(Color.GREEN(Format.BOLD("Available")))
        else:
            self._buffer.push(Color.RED(Format.BOLD("Not Available")))
        self._buffer.push(Color.BLUE("]\n"))

    def __print_optfeature_visibility_conditions(self, package_cpv: PackageCPV,
                                                 visibility_conditions: List[PathCondition]) -> None:
        with self._buffer.scoped_indent():
            self._buffer.indented_push("Advertised when:\n")
            with self._buffer.scoped_indent():
                for i, condition in enumerate(visibility_conditions):
                    self.__print_optfeature_visibility_condition(package_cpv, condition)
                    if i != len(visibility_conditions) - 1:
                        self._buffer.push_indent()
                        self._buffer.indented_push(Format.BOLD(" or\n"))
                        self._buffer.pop_indent()

    def __print_optfeature_visibility_condition(self, package_cpv: PackageCPV,
                                                visibility_condition: PathCondition) -> None:
        if visibility_condition.installed_packages:
            self._buffer.indented_push("The following packages are installed: [")
            self.print_package_atoms(visibility_condition.installed_packages)
            self._buffer.push("]\n")

        if visibility_condition.uninstalled_packages:
            self._buffer.indented_push("The following packages are not installed: [")
            self.print_package_atoms(visibility_condition.uninstalled_packages,
                                     installed_color=Color.RED, uninstalled_color=Color.GREEN)
            self._buffer.push("]\n")

        if visibility_condition.enabled_use_flags:
            self._buffer.indented_push("The following USE flags are enabled: [")
            self.print_use_flags_to_enable_list(package_cpv, visibility_condition.enabled_use_flags)
            self._buffer.push("]\n")

        if visibility_condition.disabled_use_flags:
            self._buffer.indented_push("The following USE flags are disabled: [")
            self.print_use_flags_to_disable_list(package_cpv, visibility_condition.disabled_use_flags)
            self._buffer.push("]\n")

        if visibility_condition.successful_commands:
            self._buffer.indented_push("The following commands succeed:\n")
            with self._buffer.scoped_indent():
                self.print_commands(visibility_condition.successful_commands)

        if visibility_condition.failed_commands:
            self._buffer.indented_push("The following commands fail:\n")
            with self._buffer.scoped_indent():
                self.print_commands(visibility_condition.failed_commands)

        if visibility_condition.kernel_version_range is not None:
            self._buffer.indented_push("Kernel version in range: ")
            self.print_colored_kernel_version_range(visibility_condition.kernel_version_range)
            self._buffer.push('\n')

    def __print_packages_required_to_enable_optfeature(self, package_combinations: List[List[PackageAtom]]) -> None:
        with self._buffer.scoped_indent():
            self._buffer.indented_push("Required packages to enable the feature:\n")
            for i, package_combo in enumerate(package_combinations):
                self.print_package_combination(package_combo)

                if i != len(package_combinations) - 1:
                    self._buffer.push(Format.BOLD(" or\n"))
                else:
                    self._buffer.push('\n')
