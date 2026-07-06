from collections import defaultdict
from typing import List

from ebuild_analyzer.optfeatures.optfeature import OptFeature
from ebuild_analyzer.optfeatures.optfeature_availability_checker import OptFeatureAvailabilityChecker
from ebuild_analyzer.output.ansi import Format, Color
from ebuild_analyzer.output.output_buffer import OutputBuffer
from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.path_conditions.path_condition import PathCondition
from ebuild_analyzer.utils.portage_db import PortageDatabase


class OptFeaturesPrinter:
    def __init__(self, portage_db: PortageDatabase, show_ad_conditions: bool) -> None:
        self.__portage_db = portage_db
        self.__show_ad_conditions = show_ad_conditions
        self.__buffer = OutputBuffer()
        self.__optfeature_availability_checker = OptFeatureAvailabilityChecker(portage_db)

    def print(self, package_cpv: PackageCPV, optfeatures: List[OptFeature]) -> None:
        self.__buffer.push(Color.LIGHT_PURPLE(Format.BOLD(f"Optional features for package {package_cpv.text}:\n")))
        self.__buffer.push_indent()

        optfeatures_groups = defaultdict(list)
        for optfeature in optfeatures:
            optfeatures_groups[optfeature.header].append(optfeature)

        for header, optfeatures in optfeatures_groups.items():
            if header is not None:
                self.__buffer.indented_push(Color.BLUE(Format.BOLD(f"{header}\n")))
                self.__buffer.push_indent()

            for optfeature in optfeatures:
                self.__buffer.indented_push(Format.BOLD(optfeature.description))
                self.__print_feature_availability(optfeature)

                if optfeature.visibility_conditions and self.__show_ad_conditions:
                    self.__print_optfeature_visibility_conditions(package_cpv, optfeature.visibility_conditions)
                self.__print_packages_required_to_enable_optfeature(optfeature.possible_feature_dependencies)
                self.__buffer.push('\n')
            self.__buffer.pop_indent()
        self.__buffer.print()

    def __print_feature_availability(self, optfeature: OptFeature) -> None:
        is_feature_available = self.__optfeature_availability_checker.is_available(optfeature)

        self.__buffer.push(Color.BLUE(" ["))
        if is_feature_available:
            self.__buffer.push(Color.GREEN(Format.BOLD("Available")))
        else:
            self.__buffer.push(Color.RED(Format.BOLD("Not Available")))
        self.__buffer.push(Color.BLUE("]\n"))

    def __print_optfeature_visibility_conditions(self, package_cpv: PackageCPV,
                                                 visibility_conditions: List[PathCondition]) -> None:
        with self.__buffer.scoped_indent():
            self.__buffer.indented_push("Advertised when:\n")
            with self.__buffer.scoped_indent():
                for i, condition in enumerate(visibility_conditions):
                    self.__print_optfeature_visibility_condition(package_cpv, condition)
                    if i != len(visibility_conditions) - 1:
                        self.__buffer.push_indent()
                        self.__buffer.indented_push(Format.BOLD(" or\n"))
                        self.__buffer.pop_indent()

    def __print_optfeature_visibility_condition(self, package_cpv: PackageCPV,
                                                visibility_condition: PathCondition) -> None:
        if visibility_condition.installed_packages:
            self.__buffer.indented_push("The following packages are installed: [")
            self.__print_package_atoms(visibility_condition.installed_packages)
            self.__buffer.push("]\n")

        if visibility_condition.uninstalled_packages:
            self.__buffer.indented_push("The following packages are not installed: [")
            self.__print_package_atoms(visibility_condition.uninstalled_packages,
                                       installed_color=Color.RED, uninstalled_color=Color.GREEN)
            self.__buffer.push("]\n")

        if visibility_condition.enabled_use_flags:
            self.__buffer.indented_push("The following USE flags are enabled: [")
            self.__print_use_flags_to_enable_list(package_cpv, visibility_condition.enabled_use_flags)
            self.__buffer.push("]\n")

        if visibility_condition.disabled_use_flags:
            self.__buffer.indented_push("The following USE flags are disabled: [")
            self.__print_use_flags_to_disable_list(package_cpv, visibility_condition.disabled_use_flags)
            self.__buffer.push("]\n")

    def __print_packages_required_to_enable_optfeature(self, package_combinations: List[List[PackageAtom]]) -> None:
        with self.__buffer.scoped_indent():
            self.__buffer.indented_push("Required packages to enable the feature:\n")
            for i, package_combo in enumerate(package_combinations):
                self.__print_package_combination(package_combo)

                if i != len(package_combinations) - 1:
                    self.__buffer.push(Format.BOLD(" or\n"))
                else:
                    self.__buffer.push('\n')

    def __print_package_atoms(self, package_atoms: List[PackageAtom], installed_color: Color = Color.GREEN,
                              uninstalled_color: Color = Color.RED) -> None:
        for i, package_atom in enumerate(package_atoms):
            self.__print_package_atom(package_atom, installed_color, uninstalled_color)

            if i != len(package_atoms) - 1:
                self.__buffer.push(', ')

    def __print_package_atom(self, package_atom: PackageAtom, installed_color: Color = Color.GREEN,
                             uninstalled_color: Color = Color.RED):
        if not self.__portage_db.does_package_exist(package_atom) or self.__portage_db.is_package_masked(
                package_atom):
            self.__print_non_installable_package(package_atom)
            return

        self.__print_colored_package_atom(package_atom, installed_color, uninstalled_color)

        package_cpv = self.__get_most_relevant_cpv(package_atom)
        if package_atom.required_enabled_use_flags or package_atom.required_disabled_use_flags:
            self.__buffer.push('[')
        if package_atom.required_enabled_use_flags:
            self.__print_use_flags_to_enable_list(package_cpv, package_atom.required_enabled_use_flags)
            if package_atom.required_disabled_use_flags:
                self.__buffer.push(', ')
        if package_atom.required_disabled_use_flags:
            self.__print_use_flags_to_disable_list(package_cpv, package_atom.required_disabled_use_flags)
        if package_atom.required_enabled_use_flags or package_atom.required_disabled_use_flags:
            self.__buffer.push(']')

    def __print_use_flags_to_disable_list(self, package_cpv: PackageCPV, use_flags: List[str]) -> None:
        for i, use_flag in enumerate(use_flags):
            self.__print_colored_use_flag_to_disable(package_cpv, use_flag)

            if i != len(use_flags) - 1:
                self.__buffer.push(', ')

    def __print_use_flags_to_enable_list(self, package_cpv: PackageCPV, use_flags: List[str]) -> None:
        for i, use_flag in enumerate(use_flags):
            self.__print_colored_use_flag_to_enable(package_cpv, use_flag)

            if i != len(use_flags) - 1:
                self.__buffer.push(', ')

    def __print_package_combination(self, package_combo: List[PackageAtom]) -> None:
        with self.__buffer.scoped_indent():
            for i, package_atom in enumerate(package_combo):
                self.__buffer.indented_push("")
                self.__print_package_atom(package_atom)

                if i != len(package_combo) - 1:
                    self.__buffer.push(Format.BOLD(" and "))
                    self.__buffer.disable_indentation()
        self.__buffer.enable_indentation()

    def __print_colored_use_flag_to_disable(self, package_cpv: PackageCPV, use_flag: str) -> None:
        if not self.__portage_db.is_use_flag_enabled(package_cpv, use_flag):
            self.__buffer.push(Color.GREEN(f"-{use_flag}"))
        else:
            self.__buffer.push(Color.RED(f"-{use_flag}"))

    def __print_colored_use_flag_to_enable(self, package_cpv: PackageCPV, use_flag: str) -> None:
        if self.__portage_db.is_use_flag_enabled(package_cpv, use_flag):
            self.__buffer.push(Color.GREEN(use_flag))
        else:
            self.__buffer.push(Color.RED(use_flag))

    def __print_colored_package_atom(self, package_atom: PackageAtom, installed_color: Color = Color.GREEN,
                                     uninstalled_color: Color = Color.RED) -> None:
        if self.__portage_db.is_package_installed(package_atom):
            self.__buffer.push(installed_color(package_atom.text))
        else:
            self.__buffer.push(uninstalled_color(package_atom.text))

    def __print_non_installable_package(self, package_atom: PackageAtom) -> None:
        use_flags = ','.join(package_atom.required_enabled_use_flags)
        use_flags += ','.join(package_atom.required_disabled_use_flags)
        self.__buffer.push(f"{package_atom.text}")
        if use_flags:
            self.__buffer.push(f"[{use_flags}]")

    def __get_most_relevant_cpv(self, package_atom: PackageAtom) -> PackageCPV:
        if self.__portage_db.is_package_installed(package_atom):
            return self.__portage_db.get_best_installed_cpv(package_atom)
        else:
            return self.__portage_db.get_best_visible_cpv(package_atom)
