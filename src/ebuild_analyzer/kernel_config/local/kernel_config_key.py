from dataclasses import dataclass
from enum import StrEnum


class KernelConfigState(StrEnum):
    BUILT_IN = "y"
    MODULE = "m"
    DISABLED = "n"


@dataclass(frozen=True)
class KernelConfigKey:
    name: str
    value: str
