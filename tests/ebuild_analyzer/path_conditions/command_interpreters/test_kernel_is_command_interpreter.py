from typing import List

import pytest

from ebuild_analyzer.kernel_version.kernel_version import KernelVersion
from ebuild_analyzer.kernel_version.kernel_version_range import KernelVersionRange
from ebuild_analyzer.path_conditions.command_interpreters.kernel_is_command_interpreter import \
    KernelIsCommandInterpreter
from ebuild_analyzer.path_conditions.path_condition import PathCondition


@pytest.mark.parametrize("arguments, expected_path_condition", [
    (["2", "6", "10"], PathCondition(kernel_version_range=KernelVersionRange.exactly(KernelVersion(2, 6, 10)))),
    (["2.6.10"], PathCondition(kernel_version_range=KernelVersionRange.exactly(KernelVersion(2, 6, 10)))),
    (["-eq", "2.6.10"], PathCondition(kernel_version_range=KernelVersionRange.exactly(KernelVersion(2, 6, 10)))),
    (["-eq", "2", "6", "10"], PathCondition(kernel_version_range=KernelVersionRange.exactly(KernelVersion(2, 6, 10)))),
    (["-eq", "2", "6"], PathCondition(kernel_version_range=KernelVersionRange.exactly(KernelVersion(2, 6, 0)))),

    (["-eq", "2"], PathCondition(kernel_version_range=KernelVersionRange.exactly(KernelVersion(2, 0, 0)))),
    (["eq", "2"], PathCondition(kernel_version_range=KernelVersionRange.exactly(KernelVersion(2, 0, 0)))),
    (["-lt", "2"], PathCondition(kernel_version_range=KernelVersionRange.less_than(KernelVersion(2, 0, 0)))),
    (["lt", "2"], PathCondition(kernel_version_range=KernelVersionRange.less_than(KernelVersion(2, 0, 0)))),
    (["-gt", "2"], PathCondition(kernel_version_range=KernelVersionRange.greater_than(KernelVersion(2, 0, 0)))),
    (["gt", "2"], PathCondition(kernel_version_range=KernelVersionRange.greater_than(KernelVersion(2, 0, 0)))),
    (["-ge", "2"], PathCondition(kernel_version_range=KernelVersionRange.at_least(KernelVersion(2, 0, 0)))),
    (["ge", "2"], PathCondition(kernel_version_range=KernelVersionRange.at_least(KernelVersion(2, 0, 0)))),
    (["-le", "2"], PathCondition(kernel_version_range=KernelVersionRange.at_most(KernelVersion(2, 0, 0)))),
    (["le", "2"], PathCondition(kernel_version_range=KernelVersionRange.at_most(KernelVersion(2, 0, 0)))),
])
def test_sanity(arguments: List[str], expected_path_condition: PathCondition):
    assert KernelIsCommandInterpreter().create_path_conditions(arguments) == expected_path_condition
