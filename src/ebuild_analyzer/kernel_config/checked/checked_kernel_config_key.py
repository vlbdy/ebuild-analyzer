from dataclasses import dataclass, field
from typing import List

from ebuild_analyzer.path_conditions.path_condition import PathCondition
from ebuild_analyzer.utils.conditional_message import ConditionalMessage


@dataclass
class CheckedKernelConfigKey:
    name: str
    enabled: bool
    required: bool
    conditional_requirements: List[PathCondition] = field(default_factory=list)
    unmet_messages: List[ConditionalMessage] = field(default_factory=list)
