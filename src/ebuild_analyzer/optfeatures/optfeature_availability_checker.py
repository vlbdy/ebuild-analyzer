from ebuild_analyzer.optfeatures.optfeature import OptFeature
from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.utils.package_state_provider import PackageStateProvider


class OptFeatureAvailabilityChecker:
    def __init__(self, package_state_provider: PackageStateProvider) -> None:
        self.__package_state_provider = package_state_provider

    def is_available(self, optfeature: OptFeature) -> bool:
        return any(
            all(self.__is_package_dependency_satisfied(package_atom) for package_atom in feature_dependencies)
            for feature_dependencies in optfeature.possible_feature_dependencies
        )

    def __is_package_dependency_satisfied(self, package_atom: PackageAtom) -> bool:
        return (
                self.__package_state_provider.is_package_installed(package_atom)
                and all(self.__package_state_provider.is_use_flag_enabled(package_atom, use_flag)
                        for use_flag in package_atom.required_enabled_use_flags)
                and all(not self.__package_state_provider.is_use_flag_enabled(package_atom, use_flag)
                        for use_flag in package_atom.required_disabled_use_flags)
        )
