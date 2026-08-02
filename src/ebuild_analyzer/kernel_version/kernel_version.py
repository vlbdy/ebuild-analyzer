from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class KernelVersion:
    major: int
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
