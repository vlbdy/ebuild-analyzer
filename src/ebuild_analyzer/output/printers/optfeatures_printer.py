from collections import defaultdict
from typing import List

from ebuild_analyzer.extractors.optfeature import OptFeature, PackageWithUses
from ebuild_analyzer.output.ansi import Format, Color
from ebuild_analyzer.output.output_buffer import OutputBuffer
from ebuild_analyzer.path_conditions.path_condition import PathCondition
from ebuild_analyzer.utils.portage_db import PortageDatabase


class OptFeaturesPrinter:
    def __init__(self, portage_db: PortageDatabase, show_ad_conditions: bool) -> None:
        self.__portage_db = portage_db
        self.show_ad_conditions = show_ad_conditions
        self.__buffer = OutputBuffer()

    def print_optfeatures(self, target_package: str, optfeatures: List[OptFeature]) -> None:
        self.__buffer.push(Color.LIGHT_PURPLE(Format.BOLD(f"Optional features for package {target_package}:\n")))
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

                if optfeature.visibility_conditions and self.show_ad_conditions:
                    self.__print_optfeature_visibility_conditions(target_package, optfeature.visibility_conditions)
                self.__print_packages_required_to_enable_optfeature(optfeature.possible_feature_dependencies)
                self.__buffer.push('\n')
            self.__buffer.pop_indent()
        self.__buffer.print()

    def __print_feature_availability(self, optfeature: OptFeature) -> None:
        is_feature_available = self.__is_feature_available(optfeature)

        self.__buffer.push(Color.BLUE(" ["))
        if is_feature_available:
            self.__buffer.push(Color.GREEN(Format.BOLD("Available")))
        else:
            self.__buffer.push(Color.RED(Format.BOLD("Not Available")))
        self.__buffer.push(Color.BLUE("]\n"))

    def __is_feature_available(self, optfeature: OptFeature) -> bool:
        for feature_dependencies in optfeature.possible_feature_dependencies:
            feature_dependencies_installed = True
            for package in feature_dependencies:
                if not self.__portage_db.is_package_installed(package.package_name):
                    feature_dependencies_installed = False
                    break
                if package.enabled_use_flags:
                    for use_flag in package.enabled_use_flags:
                        if not self.__portage_db.is_use_flag_enabled(package.package_name, use_flag):
                            feature_dependencies_installed = False

            if feature_dependencies_installed:
                return True
        return False

    def __print_optfeature_visibility_conditions(self, target_package: str,
                                                 visibility_conditions: List[PathCondition]) -> None:
        with self.__buffer.scoped_indent():
            self.__buffer.indented_push("Advertised when:\n")
            with self.__buffer.scoped_indent():
                for i, condition in enumerate(visibility_conditions):
                    self.__print_optfeature_visibility_condition(target_package, condition)
                    if i != len(visibility_conditions) - 1:
                        self.__buffer.push_indent()
                        self.__buffer.indented_push(Format.BOLD(" or\n"))
                        self.__buffer.pop_indent()

    def __print_optfeature_visibility_condition(self, target_package: str, visibility_condition: PathCondition) -> None:
        if visibility_condition.installed_packages:
            self.__buffer.indented_push("The following packages are installed: [")
            self.__print_packages_list(visibility_condition.installed_packages)
            self.__buffer.push("]\n")

        if visibility_condition.uninstalled_packages:
            self.__buffer.indented_push("The following packages are not installed: [")
            self.__print_packages_list(visibility_condition.uninstalled_packages,
                                       installed_color=Color.RED, uninstalled_color=Color.GREEN)
            self.__buffer.push("]\n")

        if visibility_condition.enabled_use_flags:
            self.__buffer.indented_push("The following USE flags are enabled: [")
            self.__print_use_flags_to_enable_list(target_package, visibility_condition.enabled_use_flags)
            self.__buffer.push("]\n")

        if visibility_condition.disabled_use_flags:
            self.__buffer.indented_push("The following USE flags are disabled: [")
            self.__print_use_flags_to_disable_list(target_package, visibility_condition.disabled_use_flags)
            self.__buffer.push("]\n")

    def __print_packages_required_to_enable_optfeature(self, package_combinations: List[List[PackageWithUses]]) -> None:
        with self.__buffer.scoped_indent():
            self.__buffer.indented_push("Required packages to enable the feature:\n")
            for i, package_combo in enumerate(package_combinations):
                self.__print_package_combination(package_combo)

                if i != len(package_combinations) - 1:
                    self.__buffer.push(Format.BOLD(" or\n"))
                else:
                    self.__buffer.push('\n')

    def __print_packages_list(self, packages: List[str], installed_color: Color = Color.GREEN,
                              uninstalled_color: Color = Color.RED) -> None:
        for i, package in enumerate(packages):
            self.__print_colored_package_name(package, installed_color, uninstalled_color)

            if i != len(packages) - 1:
                self.__buffer.push(', ')

    def __print_use_flags_to_disable_list(self, target_package: str, use_flags: List[str]) -> None:
        for i, use_flag in enumerate(use_flags):
            self.__print_colored_use_flag_to_disable(target_package, use_flag)

            if i != len(use_flags) - 1:
                self.__buffer.push(', ')

    def __print_use_flags_to_enable_list(self, target_package: str, use_flags: List[str]) -> None:
        for i, use_flag in enumerate(use_flags):
            self.__print_colored_use_flag_to_enable(target_package, use_flag)

            if i != len(use_flags) - 1:
                self.__buffer.push(', ')

    def __print_package_combination(self, package_combo: List[PackageWithUses]) -> None:
        with self.__buffer.scoped_indent():
            for i, package in enumerate(package_combo):
                self.__buffer.indented_push("")
                self.__print_colored_package_name(package.package_name)

                if package.enabled_use_flags or package.disabled_use_flags:
                    self.__buffer.push('[')
                if package.enabled_use_flags:
                    self.__print_use_flags_to_enable_list(package.package_name, package.enabled_use_flags)
                    if package.disabled_use_flags:
                        self.__buffer.push(', ')
                if package.disabled_use_flags:
                    self.__print_use_flags_to_disable_list(package.package_name, package.disabled_use_flags)
                if package.enabled_use_flags or package.disabled_use_flags:
                    self.__buffer.push(']')

                if i != len(package_combo) - 1:
                    self.__buffer.push(Format.BOLD(" and "))
                    self.__buffer.disable_indentation()
        self.__buffer.enable_indentation()

    def __print_colored_use_flag_to_disable(self, target_package: str, use_flag: str) -> None:
        if not self.__portage_db.is_use_flag_enabled(target_package, use_flag):
            self.__buffer.push(Color.GREEN(f"-{use_flag}"))
        else:
            self.__buffer.push(Color.RED(f"-{use_flag}"))

    def __print_colored_use_flag_to_enable(self, target_package: str, use_flag: str) -> None:
        if self.__portage_db.is_use_flag_enabled(target_package, use_flag):
            self.__buffer.push(Color.GREEN(use_flag))
        else:
            self.__buffer.push(Color.RED(use_flag))

    def __print_colored_package_name(self, package: str, installed_color: Color = Color.GREEN,
                                     uninstalled_color: Color = Color.RED) -> None:
        if self.__portage_db.is_package_installed(package):
            self.__buffer.push(installed_color(package))
        else:
            self.__buffer.push(uninstalled_color(package))
