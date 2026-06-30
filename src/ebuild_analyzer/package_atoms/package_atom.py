from dataclasses import dataclass
from typing import List


@dataclass
class PackageAtom:
    text: str
    required_enabled_use_flags: List[str]
    required_disabled_use_flags: List[str]
