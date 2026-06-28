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
