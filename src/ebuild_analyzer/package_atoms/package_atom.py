from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class PackageAtom:
    text: str
    required_enabled_use_flags: List[str] = field(default_factory=list)
    required_disabled_use_flags: List[str] = field(default_factory=list)

    def __eq__(self, other: PackageAtom) -> bool:
        return (self.text == other.text
                and set(self.required_enabled_use_flags) == set(other.required_enabled_use_flags)
                and set(self.required_disabled_use_flags) == set(other.required_disabled_use_flags))

    def __hash__(self) -> int:
        return hash((self.text, tuple(self.required_enabled_use_flags), tuple(self.required_disabled_use_flags)))
