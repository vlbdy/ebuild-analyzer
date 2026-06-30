from dataclasses import dataclass
from typing import List, Optional

from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.path_conditions.path_condition import PathCondition


@dataclass(frozen=True)
class OptFeature:
    visibility_conditions: List[PathCondition]

    header: Optional[str]

    description: str
    possible_feature_dependencies: List[List[PackageAtom]]
