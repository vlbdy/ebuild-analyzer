import subprocess
from typing import List

from ebuild_analyzer.kernel_version.local_kernel_version import get_local_kernel_version
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.path_conditions.path_condition import PathCondition
from ebuild_analyzer.utils.portage_db import PortageDatabase


class PathConditionsEvaluator:
    def __init__(self, portage_db: PortageDatabase, run_unknown_commands: bool) -> None:
        self.__portage_db = portage_db
        self.__run_unknown_commands = run_unknown_commands

    def are_satisfied(self, package_cpv: PackageCPV, conditions: List[PathCondition]) -> bool:
        if not conditions:
            return True

        for condition in conditions:
            if (self.are_enabled_use_flags_satisfied(package_cpv, condition)
                    and self.are_disabled_use_flags_satisfied(package_cpv, condition)
                    and self.are_installed_packages_satisfied(condition)
                    and self.are_uninstalled_packages_satisfied(condition)
                    and self.are_successful_commands_satisfied(condition)
                    and self.are_failed_commands_satisfied(condition)
                    and self.is_kernel_version_range_satisfied(condition)):
                return True
        return False

    def are_enabled_use_flags_satisfied(self, package_cpv: PackageCPV, condition: PathCondition) -> bool:
        for use_flag in condition.enabled_use_flags:
            if not self.__portage_db.is_use_flag_enabled(package_cpv, use_flag):
                return False
        return True

    def are_disabled_use_flags_satisfied(self, package_cpv: PackageCPV, condition: PathCondition) -> bool:
        for use_flag in condition.disabled_use_flags:
            if self.__portage_db.is_use_flag_enabled(package_cpv, use_flag):
                return False
        return True

    def are_installed_packages_satisfied(self, condition: PathCondition) -> bool:
        for package_atom in condition.installed_packages:
            if not self.__portage_db.is_package_installed(package_atom):
                return False
        return True

    def are_uninstalled_packages_satisfied(self, condition: PathCondition) -> bool:
        for package_atom in condition.uninstalled_packages:
            if self.__portage_db.is_package_installed(package_atom):
                return False
        return True

    def are_successful_commands_satisfied(self, condition: PathCondition) -> bool:
        if not condition.successful_commands:
            return True
        if not self.__run_unknown_commands:
            return False

        for command in condition.successful_commands:
            result = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                return False
        return True

    def are_failed_commands_satisfied(self, condition: PathCondition) -> bool:
        if not condition.failed_commands:
            return True
        if not self.__run_unknown_commands:
            return False

        for command in condition.failed_commands:
            result = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                return False
        return True

    @staticmethod
    def is_kernel_version_range_satisfied(condition: PathCondition) -> bool:
        if condition.kernel_version_range is None:
            return True
        return condition.kernel_version_range.contains(get_local_kernel_version())
