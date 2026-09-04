from typing import List

import pytest

from ebuild_analyzer.path_conditions import path_condition_utils
from ebuild_analyzer.path_conditions.path_condition import PathCondition


@pytest.mark.parametrize("first, second, expected", [
    (
            [PathCondition(enabled_use_flags={"a"}, disabled_use_flags={"b"})],
            [PathCondition(successful_commands={"cmd"}, failed_commands={"cmd2"})],
            [PathCondition(enabled_use_flags={"a"}, disabled_use_flags={"b"}, successful_commands={"cmd"},
                           failed_commands={"cmd2"})]
    ),
    (
            [PathCondition(enabled_use_flags={"a"}), PathCondition(disabled_use_flags={"b"})],
            [PathCondition(successful_commands={"cmd"}), PathCondition(failed_commands={"cmd2"})],
            [PathCondition(enabled_use_flags={"a"}, successful_commands={"cmd"}),
             PathCondition(enabled_use_flags={"a"}, failed_commands={"cmd2"}),
             PathCondition(disabled_use_flags={"b"}, successful_commands={"cmd"}),
             PathCondition(disabled_use_flags={"b"}, failed_commands={"cmd2"})]
    ),
    (
            [PathCondition(enabled_use_flags={"a"}), PathCondition(disabled_use_flags={"b"})],
            [PathCondition(successful_commands={"cmd"})],
            [PathCondition(enabled_use_flags={"a"}, successful_commands={"cmd"}),
             PathCondition(disabled_use_flags={"b"}, successful_commands={"cmd"})]
    ),
    (
            [PathCondition(enabled_use_flags={"a"}, disabled_use_flags={"b"})],
            [],
            [PathCondition(enabled_use_flags={"a"}, disabled_use_flags={"b"})]
    ),
    (
            [PathCondition(enabled_use_flags={"a"}), PathCondition(disabled_use_flags={"b"})],
            [],
            [PathCondition(enabled_use_flags={"a"}), PathCondition(disabled_use_flags={"b"})]
    ),
    ([], [], []),
])
def test_combine_path_conditions(first: List[PathCondition], second: List[PathCondition],
                                 expected: List[PathCondition]):
    assert path_condition_utils.combine_path_conditions(first, second) == expected


@pytest.mark.parametrize("conditions, expected", [
    (
            [PathCondition(enabled_use_flags={"a"}, disabled_use_flags={"b"})],
            [PathCondition(disabled_use_flags={"a"}), PathCondition(enabled_use_flags={"b"})]
    ),
    (
            [PathCondition(enabled_use_flags={"a"}), PathCondition(disabled_use_flags={"b"})],
            [PathCondition(disabled_use_flags={"a"}, enabled_use_flags={"b"})]
    ),
    ([], []),
])
def test_negate_and_combine_path_conditions(conditions: List[PathCondition], expected: List[PathCondition]):
    assert path_condition_utils.negate_and_combine_path_conditions(conditions) == expected


@pytest.mark.parametrize("conditions, expected", [
    (
            [PathCondition(enabled_use_flags={"a"}), PathCondition(enabled_use_flags={"b"})],
            [PathCondition(enabled_use_flags={"a"}), PathCondition(enabled_use_flags={"b"})]
    ),
    (
            [PathCondition(enabled_use_flags={"a"}), PathCondition(), PathCondition(enabled_use_flags={"b"})],
            [PathCondition(enabled_use_flags={"a"}), PathCondition(enabled_use_flags={"b"})]
    ),
    (
            [PathCondition()],
            []
    ),
    ([], []),
])
def test_remove_empty_path_conditions(conditions: List[PathCondition], expected: List[PathCondition]):
    assert path_condition_utils.remove_empty_path_conditions(conditions) == expected


@pytest.mark.parametrize("conditions, expected", [
    (
            [PathCondition(enabled_use_flags={"a"}), PathCondition(enabled_use_flags={"b"})],
            [PathCondition(enabled_use_flags={"a"}), PathCondition(enabled_use_flags={"b"})]
    ),
    (
            [PathCondition(enabled_use_flags={"a"}), PathCondition(enabled_use_flags={"a"}),
             PathCondition(enabled_use_flags={"b"})],
            [PathCondition(enabled_use_flags={"a"}), PathCondition(enabled_use_flags={"b"})]
    ),
    (
            [PathCondition(enabled_use_flags={"a"}), PathCondition(enabled_use_flags={"a"})],
            [PathCondition(enabled_use_flags={"a"})]
    ),
    ([], []),
])
def test_remove_duplicate_path_conditions(conditions: List[PathCondition], expected: List[PathCondition]):
    assert path_condition_utils.remove_duplicate_path_conditions(conditions) == expected
