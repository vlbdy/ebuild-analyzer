from typing import List

import pytest

from ebuild_analyzer.path_conditions.command_interpreters.use_command_interpreter import UseCommandInterpreter
from ebuild_analyzer.path_conditions.path_condition import PathCondition


@pytest.mark.parametrize("arguments, expected_path_condition", [
    (["flag"], PathCondition(enabled_use_flags={"flag"})),
    (["!flag"], PathCondition(disabled_use_flags={"flag"})),
])
def test_sanity(arguments: List[str], expected_path_condition: PathCondition):
    assert UseCommandInterpreter().create_path_conditions(arguments) == expected_path_condition
