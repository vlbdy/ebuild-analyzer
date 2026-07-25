from typing import List

from ebuild_analyzer.path_conditions.command_interpreters.command_interpreter import CommandInterpreter
from ebuild_analyzer.path_conditions.path_condition import PathCondition


class UseCommandInterpreter(CommandInterpreter):
    def create_path_conditions(self, arguments: List[str]) -> PathCondition:
        path_condition = PathCondition()

        use_flag = arguments[0]
        if use_flag.startswith('!'):
            path_condition.disabled_use_flags.add(use_flag[1:])
        else:
            path_condition.enabled_use_flags.add(use_flag)

        return path_condition
