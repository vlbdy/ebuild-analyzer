from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class OptFeatureDependencies:
    enabled_use_flags: List[str]
    disabled_use_flags: List[str]
    package_dependencies: List[str]

@dataclass(frozen=True)
class OptFeature:
    dependencies: Optional[OptFeatureDependencies]

    header: Optional[str]

    description: str
    feature_enabling_package_combinations: List[List[str]]
