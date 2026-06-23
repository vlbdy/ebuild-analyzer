from collections import defaultdict
from typing import List

from output.ansi import Format, Color
from parser.optfeature import OptFeature, OptFeatureDependencies, PackageWithUses
from utils.portage_db import PortageDatabase


class OptFeaturesPrinter:
    def __init__(self, portage_db: PortageDatabase) -> None:
        self.__portage_db = portage_db

    def print_optfeatures(self, target_package: str, optfeatures: List[OptFeature]) -> None:
        print(Color.LIGHT_PURPLE(Format.BOLD(f"Optional features for package {target_package}:")), end='')

        optfeatures_groups = defaultdict(list)
        for optfeature in optfeatures:
            optfeatures_groups[optfeature.header].append(optfeature)

        for header, optfeatures in optfeatures_groups.items():
            print()
            indentation = 0
            if header is not None:
                print(Color.BLUE(Format.BOLD(header)))
                indentation += 4

            for optfeature in optfeatures:
                print(f"{' ' * indentation}{Format.BOLD(optfeature.description)} ", end='')
                self.__print_feature_availability(target_package, optfeature)

                if optfeature.dependencies:
                    self.__print_optfeature_dependencies(target_package, optfeature.dependencies, indentation)
                self.__print_package_required_to_enable_optfeature(optfeature.feature_enabling_package_combinations,
                                                                   indentation)
                print()

    def __print_feature_availability(self, target_package: str, optfeature: OptFeature) -> None:
        is_feature_available = self.__is_feature_available(target_package, optfeature)

        print(Color.BLUE('['), end='')
        if is_feature_available:
            print(Color.GREEN(Format.BOLD("Available")), end='')
        else:
            print(Color.RED(Format.BOLD("Not Available")), end='')
        print(Color.BLUE(']'))

    def __is_feature_available(self, target_package: str, optfeature: OptFeature) -> bool:
        if optfeature.dependencies:
            for dependency in optfeature.dependencies.package_dependencies:
                if not self.__portage_db.is_package_installed(dependency):
                    return False
            for use_flag_to_enable in optfeature.dependencies.enabled_use_flags:
                if not self.__portage_db.is_use_flag_enabled(target_package, use_flag_to_enable):
                    return False
            for use_flag_to_disable in optfeature.dependencies.disabled_use_flags:
                if self.__portage_db.is_use_flag_enabled(target_package, use_flag_to_disable):
                    return False

        for package_combination in optfeature.feature_enabling_package_combinations:
            package_combination_installed = True
            for package in package_combination:
                if not self.__portage_db.is_package_installed(package.package_name):
                    package_combination_installed = False
                    break
                if package.enabled_use_flags:
                    for use_flag in package.enabled_use_flags:
                        if not self.__portage_db.is_use_flag_enabled(package.package_name, use_flag):
                            package_combination_installed = False

            if package_combination_installed:
                return True
        return False

    def __print_optfeature_dependencies(self, target_package: str, optfeature_dependencies: OptFeatureDependencies,
                                        base_indentation: int) -> None:
        indentation = base_indentation + 4
        if optfeature_dependencies.package_dependencies:
            print(f"{' ' * indentation}Depends on packages: [", end='')
            self.__print_packages_list(optfeature_dependencies.package_dependencies)
            print(']')

        if optfeature_dependencies.enabled_use_flags:
            print(f"{' ' * indentation}USE flags to enable: [", end='')
            self.__print_use_flags_to_enable_list(target_package, optfeature_dependencies.enabled_use_flags)
            print(']')

        if optfeature_dependencies.disabled_use_flags:
            print(f"{' ' * indentation}USE flags to disable: [", end='')
            self.__print_use_flags_to_disable_list(target_package, optfeature_dependencies.disabled_use_flags)
            print(']')

    def __print_package_required_to_enable_optfeature(self, package_combinations: List[List[PackageWithUses]],
                                                      base_indentation: int) -> None:
        indentation = base_indentation + 4
        print(f"{' ' * indentation}Required packages to enable the feature:")
        for i, package_combo in enumerate(package_combinations):
            self.__print_package_combination(package_combo, indentation)

            if i != len(package_combinations) - 1:
                print(Format.BOLD(" or"))
            else:
                print()

    def __print_packages_list(self, packages: List[str]) -> None:
        for i, dependency in enumerate(packages):
            self.__print_colored_package_name(dependency, 0)

            if i != len(packages) - 1:
                print(', ', end='')

    def __print_use_flags_to_disable_list(self, target_package: str, use_flags: List[str]) -> None:
        for i, use_flag in enumerate(use_flags):
            self.__print_colored_use_flag_to_disable(target_package, use_flag)

            if i != len(use_flags) - 1:
                print(', ', end='')

    def __print_use_flags_to_enable_list(self, target_package: str, use_flags: List[str]) -> None:
        for i, use_flag in enumerate(use_flags):
            self.__print_colored_use_flag_to_enable(target_package, use_flag)

            if i != len(use_flags) - 1:
                print(', ', end='')

    def __print_package_combination(self, package_combo: List[PackageWithUses], base_indentation: int) -> None:
        indentation = base_indentation + 4
        for i, package in enumerate(package_combo):
            self.__print_colored_package_name(package.package_name, indentation)

            if package.enabled_use_flags or package.disabled_use_flags:
                print('[', end='')
            if package.enabled_use_flags:
                self.__print_use_flags_to_enable_list(package.package_name, package.enabled_use_flags)
                if package.disabled_use_flags:
                    print(', ', end='')
            if package.disabled_use_flags:
                self.__print_use_flags_to_disable_list(package.package_name, package.disabled_use_flags)
            if package.enabled_use_flags or package.disabled_use_flags:
                print(']', end='')

            if i != len(package_combo) - 1:
                print(Format.BOLD(" and "), end='')
                indentation = 0

    def __print_colored_use_flag_to_disable(self, target_package: str, use_flag: str) -> None:
        if not self.__portage_db.is_use_flag_enabled(target_package, use_flag):
            print(Color.GREEN(f"-{use_flag}"), end='')
        else:
            print(Color.RED(f"-{use_flag}"), end='')

    def __print_colored_use_flag_to_enable(self, target_package: str, use_flag: str) -> None:
        if self.__portage_db.is_use_flag_enabled(target_package, use_flag):
            print(Color.GREEN(use_flag), end='')
        else:
            print(Color.RED(use_flag), end='')

    def __print_colored_package_name(self, package: str, indentation: int) -> None:
        if self.__portage_db.is_package_installed(package):
            print(f"{' ' * indentation}{Color.GREEN(package)}", end='')
        else:
            print(f"{' ' * indentation}{Color.RED(package)}", end='')
