from dataclasses import dataclass, field
from typing import List


@dataclass
class PathConditions:
    enabled_use_flags: List[str] = field(default_factory=list)
    disabled_use_flags: List[str] = field(default_factory=list)
    installed_packages: List[str] = field(default_factory=list)
    uninstalled_packages: List[str] = field(default_factory=list)

    def __iadd__(self, other: PathConditions) -> PathConditions:
        self.enabled_use_flags += other.enabled_use_flags
        self.disabled_use_flags += other.disabled_use_flags
        self.installed_packages += other.installed_packages
        self.uninstalled_packages += other.uninstalled_packages
        return self

    # Commands can be negated in bash with '!', this is a helper method
    def negated_add(self, other: PathConditions) -> PathConditions:
        self.enabled_use_flags += other.disabled_use_flags
        self.disabled_use_flags += other.enabled_use_flags
        self.installed_packages += other.uninstalled_packages
        self.uninstalled_packages += other.installed_packages
        return self
