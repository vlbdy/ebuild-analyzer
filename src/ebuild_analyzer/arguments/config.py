from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Config:
    command: str
    package: Optional[str]

    all: bool
    verbose: bool
    show_ad_conditions: bool
    run_unknown_commands: bool
