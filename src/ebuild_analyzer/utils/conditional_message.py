from dataclasses import dataclass
from enum import StrEnum
from typing import List

from ebuild_analyzer.path_conditions.path_condition import PathCondition


class MessageSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


@dataclass
class ConditionalMessage:
    message: str
    severity: MessageSeverity
    conditions: List[PathCondition]
