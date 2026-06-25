from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class PackageWithUses:
    package_name: str
    enabled_use_flags: Optional[List[str]]
    disabled_use_flags: Optional[List[str]]


@dataclass
class OptFeatureDependencies:
    enabled_use_flags: List[str] = field(default_factory=list)
    disabled_use_flags: List[str] = field(default_factory=list)
    installed_package_dependencies: List[str] = field(default_factory=list)
    uninstalled_package_dependencies: List[str] = field(default_factory=list)

    def __iadd__(self, other: OptFeatureDependencies) -> OptFeatureDependencies:
        self.enabled_use_flags += other.enabled_use_flags
        self.disabled_use_flags += other.disabled_use_flags
        self.installed_package_dependencies += other.installed_package_dependencies
        self.uninstalled_package_dependencies += other.uninstalled_package_dependencies
        return self

    # Commands can be negated in bash with '!', this is a helper method
    def negated_add(self, other: OptFeatureDependencies) -> OptFeatureDependencies:
        self.enabled_use_flags += other.disabled_use_flags
        self.disabled_use_flags += other.enabled_use_flags
        self.installed_package_dependencies += other.uninstalled_package_dependencies
        self.uninstalled_package_dependencies += other.installed_package_dependencies
        return self


@dataclass(frozen=True)
class OptFeature:
    dependencies: OptFeatureDependencies

    header: Optional[str]

    description: str
    feature_enabling_package_combinations: List[List[PackageWithUses]]
