from copy import copy
from dataclasses import dataclass, field
from typing import List


@dataclass
class PathCondition:
    enabled_use_flags: List[str] = field(default_factory=list)
    disabled_use_flags: List[str] = field(default_factory=list)
    installed_packages: List[str] = field(default_factory=list)
    uninstalled_packages: List[str] = field(default_factory=list)

    def __iadd__(self, other: PathCondition) -> PathCondition:
        self.enabled_use_flags += other.enabled_use_flags
        self.disabled_use_flags += other.disabled_use_flags
        self.installed_packages += other.installed_packages
        self.uninstalled_packages += other.uninstalled_packages
        return self

    def __add__(self, other: PathCondition) -> PathCondition:
        new_path_conditions = copy(self)
        new_path_conditions += other
        return new_path_conditions

    def __bool__(self) -> bool:
        return bool(
            self.enabled_use_flags or self.disabled_use_flags or self.installed_packages or self.uninstalled_packages)

    # Commands can be negated in bash with '!', this is a helper method
    def negated_add(self, other: PathCondition) -> PathCondition:
        self.enabled_use_flags += other.disabled_use_flags
        self.disabled_use_flags += other.enabled_use_flags
        self.installed_packages += other.uninstalled_packages
        self.uninstalled_packages += other.installed_packages
        return self

    # De Morgan negation
    def negate(self) -> List[PathCondition]:
        # The code is built such that a list of path conditions means the following:
        #   - Path conditions are OR'ed
        #   - The inner fields of path conditions are AND'ed
        #
        # Let's say for example that the fields in the class are a,b,c,d respectively (including their elements),
        # this means that the condition is (a && b && c && d). The negation is (!a || !b || !c || !d).

        negated_conditions: List[PathCondition] = []
        for installed_package in self.installed_packages:
            negated_conditions.append(PathCondition(uninstalled_packages=[installed_package]))
        for uninstalled_package in self.uninstalled_packages:
            negated_conditions.append(PathCondition(installed_packages=[uninstalled_package]))
        for enabled_use_flag in self.enabled_use_flags:
            negated_conditions.append(PathCondition(disabled_use_flags=[enabled_use_flag]))
        for disabled_use_flag in self.disabled_use_flags:
            negated_conditions.append(PathCondition(enabled_use_flags=[disabled_use_flag]))
        return negated_conditions
