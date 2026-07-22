from dataclasses import dataclass
from typing import List

from ebuild_analyzer.path_conditions.path_condition import PathCondition


@dataclass(frozen=True)
class KernelConfigKey:
    name: str
    enabled: bool
    required: bool
    conditional_requirements: List[PathCondition]
