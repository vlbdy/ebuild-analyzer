from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class KernelVersion:
    major: int
    minor: int = 0
    patch: int = 0
