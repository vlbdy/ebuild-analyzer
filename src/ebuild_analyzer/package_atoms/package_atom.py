from dataclasses import dataclass, field
from typing import List


@dataclass
class PackageAtom:
    text: str
    required_enabled_use_flags: List[str] = field(default_factory=list)
    required_disabled_use_flags: List[str] = field(default_factory=list)
