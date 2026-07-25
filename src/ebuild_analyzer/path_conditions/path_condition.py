from dataclasses import dataclass, field
from typing import List, Set, Optional

from ebuild_analyzer.kernel_version.kernel_version_range import KernelVersionRange
from ebuild_analyzer.package_atoms.package_atom import PackageAtom


@dataclass
class PathCondition:
    enabled_use_flags: Set[str] = field(default_factory=set)
    disabled_use_flags: Set[str] = field(default_factory=set)
    installed_packages: Set[PackageAtom] = field(default_factory=set)
    uninstalled_packages: Set[PackageAtom] = field(default_factory=set)
    successful_commands: Set[str] = field(default_factory=set)
    failed_commands: Set[str] = field(default_factory=set)
    kernel_version_range: Optional[KernelVersionRange] = None

    def __iand__(self, other: PathCondition) -> PathCondition:
        self.enabled_use_flags.update(other.enabled_use_flags)
        self.disabled_use_flags.update(other.disabled_use_flags)
        self.installed_packages.update(other.installed_packages)
        self.uninstalled_packages.update(other.uninstalled_packages)
        self.successful_commands.update(other.successful_commands)
        self.failed_commands.update(other.failed_commands)
        self.kernel_version_range = KernelVersionRange.intersect(self.kernel_version_range, other.kernel_version_range)
        return self

    def __and__(self, other: PathCondition) -> PathCondition:
        return PathCondition(
            enabled_use_flags=self.enabled_use_flags | other.enabled_use_flags,
            disabled_use_flags=self.disabled_use_flags | other.disabled_use_flags,
            installed_packages=self.installed_packages | other.installed_packages,
            uninstalled_packages=self.uninstalled_packages | other.uninstalled_packages,
            successful_commands=self.successful_commands | other.successful_commands,
            failed_commands=self.failed_commands | other.failed_commands,
            kernel_version_range=KernelVersionRange.intersect(self.kernel_version_range, other.kernel_version_range),
        )

    def __bool__(self) -> bool:
        return bool(
            self.enabled_use_flags or self.disabled_use_flags or self.installed_packages or self.uninstalled_packages or
            self.successful_commands or self.failed_commands or self.kernel_version_range is not None)

    # Commands can be negated in bash with '!', this is a helper method
    def and_not(self, other: PathCondition) -> List[PathCondition]:
        path_conditions: List[PathCondition] = []

        enabled_use_flags = self.enabled_use_flags | other.disabled_use_flags
        disabled_use_flags = self.disabled_use_flags | other.enabled_use_flags
        installed_packages = self.installed_packages | other.uninstalled_packages
        uninstalled_packages = self.uninstalled_packages | other.installed_packages
        successful_commands = self.successful_commands | other.failed_commands
        failed_commands = self.failed_commands | other.successful_commands

        if other.kernel_version_range is not None:
            for other_negated_kernel_version_range in other.kernel_version_range.negate():
                new_kernel_version_range = KernelVersionRange.intersect(self.kernel_version_range,
                                                                        other_negated_kernel_version_range)
                # We don't want to have unsatisfiable path conditions
                if new_kernel_version_range.is_empty():
                    continue

                path_conditions.append(
                    PathCondition(enabled_use_flags=enabled_use_flags, disabled_use_flags=disabled_use_flags,
                                  installed_packages=installed_packages, uninstalled_packages=uninstalled_packages,
                                  successful_commands=successful_commands, failed_commands=failed_commands,
                                  kernel_version_range=new_kernel_version_range))
        else:
            path_conditions.append(
                PathCondition(enabled_use_flags=enabled_use_flags, disabled_use_flags=disabled_use_flags,
                              installed_packages=installed_packages, uninstalled_packages=uninstalled_packages,
                              successful_commands=successful_commands, failed_commands=failed_commands,
                              kernel_version_range=self.kernel_version_range))

        return path_conditions

    # De Morgan negation
    def negate(self) -> List[PathCondition]:
        # The code is built such that a list of path conditions means the following:
        #   - Path conditions are OR'ed
        #   - The inner fields of path conditions are AND'ed
        #
        # Let's say for example that the fields in the class are a,b,c,d respectively (including their elements),
        # this means that the condition is (a && b && c && d). The negation is (!a || !b || !c || !d).

        negated_conditions: List[PathCondition] = []
        for installed_package in sorted(self.installed_packages, key=lambda p: p.text):
            negated_conditions.append(PathCondition(uninstalled_packages={installed_package}))
        for uninstalled_package in sorted(self.uninstalled_packages, key=lambda p: p.text):
            negated_conditions.append(PathCondition(installed_packages={uninstalled_package}))
        for enabled_use_flag in sorted(self.enabled_use_flags):
            negated_conditions.append(PathCondition(disabled_use_flags={enabled_use_flag}))
        for disabled_use_flag in sorted(self.disabled_use_flags):
            negated_conditions.append(PathCondition(enabled_use_flags={disabled_use_flag}))
        for successful_command in sorted(self.successful_commands):
            negated_conditions.append(PathCondition(failed_commands={successful_command}))
        for failed_command in sorted(self.failed_commands):
            negated_conditions.append(PathCondition(successful_commands={failed_command}))
        if self.kernel_version_range is not None:
            for negated_kernel_version_range in self.kernel_version_range.negate():
                negated_conditions.append(PathCondition(kernel_version_range=negated_kernel_version_range))
        return negated_conditions
