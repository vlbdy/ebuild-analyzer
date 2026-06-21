from collections import defaultdict
from typing import List

from output.ansi import Format, Color
from parser.optfeature import OptFeature, OptFeatureDependencies
from utils.package_utils import is_package_installed, is_use_flag_enabled


def __print_colored_package_name(package: str, indentation: int) -> None:
    if is_package_installed(package):
        print(f"{' ' * indentation}{Color.GREEN(package)}", end='')
    else:
        print(f"{' ' * indentation}{Color.RED(package)}", end='')


def __print_colored_use_flag(target_package: str, use_flag: str) -> None:
    if is_use_flag_enabled(target_package, use_flag):
        print(Format.BOLD(Color.RED(use_flag)), end='')
    else:
        print({Format.BOLD(Color.BLUE(f"-{use_flag}"))}, end='')


def __print_package_combination(package_combo: List[str], base_indentation: int) -> None:
    indentation = base_indentation + 4
    for i, package in enumerate(package_combo):
        __print_colored_package_name(package, indentation)

        if i != len(package_combo) - 1:
            print(Format.BOLD(" and "), end='')
            indentation = 0


def __print_use_flags_list(target_package: str, use_flags: List[str]) -> None:
    for i, use_flag in enumerate(use_flags):
        __print_colored_use_flag(target_package, use_flag)

        if i != len(use_flags) - 1:
            print(', ', end='')


def __print_packages_list(packages: List[str]) -> None:
    for i, dependency in enumerate(packages):
        __print_colored_package_name(dependency, 0)

        if i != len(packages) - 1:
            print(', ', end='')


def __print_package_required_to_enable_optfeature(package_combinations: List[List[str]], base_indentation: int) -> None:
    indentation = base_indentation + 4
    print(f"{' ' * indentation}Required packages to enable the feature:")
    for i, package_combo in enumerate(package_combinations):
        __print_package_combination(package_combo, indentation)

        if i != len(package_combinations) - 1:
            print(Format.BOLD(" or"))
        else:
            print()


def __print_optfeature_dependencies(target_package: str, optfeature_dependencies: OptFeatureDependencies,
                                    base_indentation: int) -> None:
    indentation = base_indentation + 4
    if optfeature_dependencies.package_dependencies:
        print(f"{' ' * indentation}Depends on packages: [", end='')
        __print_packages_list(optfeature_dependencies.package_dependencies)
        print(']')

    if optfeature_dependencies.enabled_use_flags:
        print(f"{' ' * indentation}USE flags to enable: [", end='')
        __print_use_flags_list(target_package, optfeature_dependencies.enabled_use_flags)
        print(']')

    if optfeature_dependencies.disabled_use_flags:
        print(f"{' ' * indentation}USE flags to disable: [", end='')
        __print_use_flags_list(target_package, optfeature_dependencies.disabled_use_flags)
        print(']')


"""
Header
    Description [Available]/[Not Available]
        Depends on packages:
        USE flags to enable:
        USE flags to disable:
        Required packages to enable the feature:
            ...

<<< OR with no header >>>
      
Description [Available]/[Not Available]
    Depends on packages:
    USE flags to enable:
    USE flags to disable:
    Required packages to enable the feature:
        ...
"""


def print_optfeatures(target_package: str, optfeatures: List[OptFeature]) -> None:
    optfeatures_groups = defaultdict(list)
    for optfeature in optfeatures:
        optfeatures_groups[optfeature.header].append(optfeature)

    for header, optfeatures in optfeatures_groups.items():
        print()
        indentation = 0
        if header is not None:
            print(Format.BOLD(Color.BLUE(header)))
            indentation += 4

        for optfeature in optfeatures:
            print(f"{' ' * indentation}{Format.BOLD(optfeature.description)}")
            if optfeature.dependencies:
                __print_optfeature_dependencies(target_package, optfeature.dependencies, indentation)
            __print_package_required_to_enable_optfeature(optfeature.feature_enabling_package_combinations, indentation)
