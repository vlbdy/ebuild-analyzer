from dataclasses import dataclass
from typing import List, Optional

from ebuild_analyzer.path_conditions.path_conditions import PathConditions


@dataclass(frozen=True)
class PackageWithUses:
    package_name: str
    enabled_use_flags: Optional[List[str]]
    disabled_use_flags: Optional[List[str]]


@dataclass(frozen=True)
class OptFeature:
    visibility_conditions: PathConditions

    header: Optional[str]

    description: str
    possible_feature_dependencies: List[List[PackageWithUses]]
