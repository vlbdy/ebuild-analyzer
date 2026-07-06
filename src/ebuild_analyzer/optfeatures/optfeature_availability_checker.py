from ebuild_analyzer.optfeatures.optfeature import OptFeature
from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.utils.portage_db import PortageDatabase


class OptFeatureAvailabilityChecker:
    def __init__(self, portage_db: PortageDatabase) -> None:
        self.__portage_db = portage_db

    def is_available(self, optfeature: OptFeature) -> bool:
        return any(
            all(self.__is_package_dependency_satisfied(package_atom) for package_atom in feature_dependencies)
            for feature_dependencies in optfeature.possible_feature_dependencies
        )

    def __is_package_dependency_satisfied(self, package_atom: PackageAtom) -> bool:
        if not self.__portage_db.is_package_installed(package_atom):
            return False

        package_cpv = self.__portage_db.get_best_installed_cpv(package_atom)
        return (
                all(self.__portage_db.is_use_flag_enabled(package_cpv, use_flag)
                    for use_flag in package_atom.required_enabled_use_flags)
                and all(not self.__portage_db.is_use_flag_enabled(package_cpv, use_flag)
                        for use_flag in package_atom.required_disabled_use_flags)
        )
