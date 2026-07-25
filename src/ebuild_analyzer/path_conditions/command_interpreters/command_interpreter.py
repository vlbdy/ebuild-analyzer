from typing import Protocol, List

from ebuild_analyzer.path_conditions.path_condition import PathCondition


class CommandInterpreter(Protocol):
    def create_path_conditions(self, arguments: List[str]) -> PathCondition: ...
