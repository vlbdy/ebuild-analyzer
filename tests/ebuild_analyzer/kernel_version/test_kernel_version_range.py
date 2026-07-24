from typing import Set, Optional

import pytest

from ebuild_analyzer.kernel_version.kernel_version import KernelVersion
from ebuild_analyzer.kernel_version.kernel_version_range import KernelVersionRange


@pytest.mark.parametrize("kernel_version_range, expected_result", [
    (KernelVersionRange.unlimited(), True),
    (KernelVersionRange.at_least(KernelVersion(1)), False),
    (KernelVersionRange.empty(), False),
])
def test_is_unlimited(kernel_version_range: KernelVersionRange, expected_result: bool):
    assert kernel_version_range.is_unlimited() == expected_result


@pytest.mark.parametrize("kernel_version_range, expected_result", [
    (KernelVersionRange.unlimited(), False),
    (KernelVersionRange.at_least(KernelVersion(1)), False),
    (KernelVersionRange.between(KernelVersion(1), KernelVersion(2)), False),
    (KernelVersionRange.between(KernelVersion(1), KernelVersion(1), min_inclusive=False, max_inclusive=False), True),
    (KernelVersionRange.between(KernelVersion(1), KernelVersion(1), min_inclusive=True, max_inclusive=False), True),
    (KernelVersionRange.between(KernelVersion(1), KernelVersion(1), min_inclusive=False, max_inclusive=True), True),
    (KernelVersionRange.exactly(KernelVersion(1)), False),
    (KernelVersionRange.empty(), True),
])
def test_is_empty(kernel_version_range: KernelVersionRange, expected_result: bool):
    assert kernel_version_range.is_empty() == expected_result


@pytest.mark.parametrize("kernel_version_range, kernel_version, expected_result", [
    (KernelVersionRange.unlimited(), KernelVersion(1), True),
    (KernelVersionRange.empty(), KernelVersion(1), False),
    (KernelVersionRange.exactly(KernelVersion(1)), KernelVersion(1), True),
    (KernelVersionRange.between(KernelVersion(1), KernelVersion(2)), KernelVersion(1), True),
    (KernelVersionRange.between(KernelVersion(1), KernelVersion(2)), KernelVersion(0), False),
])
def test_contains(kernel_version_range: KernelVersionRange, kernel_version: KernelVersion, expected_result: bool):
    assert kernel_version_range.contains(kernel_version) == expected_result


@pytest.mark.parametrize("kernel_version_range, expected_result", [
    (KernelVersionRange.unlimited(), {KernelVersionRange.empty()}),
    (KernelVersionRange.empty(), {KernelVersionRange.unlimited()}),
    (KernelVersionRange.at_least(KernelVersion(1)), {KernelVersionRange.less_than(KernelVersion(1))}),
    (KernelVersionRange.greater_than(KernelVersion(1)), {KernelVersionRange.at_most(KernelVersion(1))}),
    (KernelVersionRange.at_most(KernelVersion(1)), {KernelVersionRange.greater_than(KernelVersion(1))}),
    (KernelVersionRange.less_than(KernelVersion(1)), {KernelVersionRange.at_least(KernelVersion(1))}),
    (KernelVersionRange.exactly(KernelVersion(1)),
     {KernelVersionRange.less_than(KernelVersion(1)), KernelVersionRange.greater_than(KernelVersion(1))}),
    (KernelVersionRange.between(KernelVersion(1), KernelVersion(2)),
     {KernelVersionRange.less_than(KernelVersion(1)), KernelVersionRange.at_least(KernelVersion(2))})
])
def test_negate(kernel_version_range: KernelVersionRange, expected_result: Set[KernelVersionRange]):
    assert kernel_version_range.negate() == expected_result


@pytest.mark.parametrize("kernel_version_range1, kernel_version_range2, expected_result", [
    (KernelVersionRange.unlimited(), KernelVersionRange.empty(), KernelVersionRange.empty()),
    (KernelVersionRange.unlimited(), KernelVersionRange.unlimited(), KernelVersionRange.unlimited()),
    (KernelVersionRange.at_least(KernelVersion(1)), KernelVersionRange.unlimited(),
     KernelVersionRange.at_least(KernelVersion(1))),
    (KernelVersionRange.at_most(KernelVersion(1)), KernelVersionRange.unlimited(),
     KernelVersionRange.at_most(KernelVersion(1))),
    (KernelVersionRange.exactly(KernelVersion(1)), KernelVersionRange.at_least(KernelVersion(0)),
     KernelVersionRange.exactly(KernelVersion(1))),
    (KernelVersionRange.at_least(KernelVersion(1)), KernelVersionRange.at_most(KernelVersion(3)),
     KernelVersionRange.between(KernelVersion(1), KernelVersion(3), min_inclusive=True, max_inclusive=True)),
])
def test_iand(kernel_version_range1: KernelVersionRange, kernel_version_range2: KernelVersionRange,
              expected_result: KernelVersionRange):
    kernel_version_range1 &= kernel_version_range2
    assert kernel_version_range1 == expected_result


@pytest.mark.parametrize("kernel_version_range1, kernel_version_range2, expected_result", [
    (KernelVersionRange.unlimited(), KernelVersionRange.empty(), KernelVersionRange.empty()),
    (KernelVersionRange.unlimited(), KernelVersionRange.unlimited(), KernelVersionRange.unlimited()),
    (KernelVersionRange.at_least(KernelVersion(1)), KernelVersionRange.unlimited(),
     KernelVersionRange.at_least(KernelVersion(1))),
    (KernelVersionRange.at_most(KernelVersion(1)), KernelVersionRange.unlimited(),
     KernelVersionRange.at_most(KernelVersion(1))),
    (KernelVersionRange.exactly(KernelVersion(1)), KernelVersionRange.at_least(KernelVersion(0)),
     KernelVersionRange.exactly(KernelVersion(1))),
    (KernelVersionRange.at_least(KernelVersion(1)), KernelVersionRange.at_most(KernelVersion(3)),
     KernelVersionRange.between(KernelVersion(1), KernelVersion(3), min_inclusive=True, max_inclusive=True)),
])
def test_and(kernel_version_range1: KernelVersionRange, kernel_version_range2: KernelVersionRange,
             expected_result: KernelVersionRange):
    assert (kernel_version_range1 & kernel_version_range2) == expected_result


@pytest.mark.parametrize("kernel_version_range1, kernel_version_range2, expected_result", [
    (KernelVersionRange.unlimited(), KernelVersionRange.unlimited(), True),
    (KernelVersionRange.unlimited(), KernelVersionRange.empty(), False),
    (KernelVersionRange.empty(), KernelVersionRange.empty(), True),
    (KernelVersionRange.empty(), KernelVersionRange.between(KernelVersion(10), KernelVersion(2)), True),
    (KernelVersionRange.between(KernelVersion(1), KernelVersion(2)),
     KernelVersionRange.between(KernelVersion(1), KernelVersion(2)), True),
])
def test_eq(kernel_version_range1: KernelVersionRange, kernel_version_range2: KernelVersionRange,
            expected_result: bool):
    result = kernel_version_range1 == kernel_version_range2
    assert result == expected_result


@pytest.mark.parametrize("kernel_version_range1, kernel_version_range2, expected_result", [
    (KernelVersionRange.between(KernelVersion(1), KernelVersion(10)),
     KernelVersionRange(KernelVersion(2), KernelVersion(8)), KernelVersionRange(KernelVersion(2), KernelVersion(8))),
    (None, KernelVersionRange.unlimited(), KernelVersionRange.unlimited()),
    (KernelVersionRange.empty(), None, KernelVersionRange.empty()),
    (None, None, None),
])
def test_intersect(kernel_version_range1: Optional[KernelVersionRange],
                   kernel_version_range2: Optional[KernelVersionRange],
                   expected_result: Optional[KernelVersionRange]):
    assert KernelVersionRange.intersect(kernel_version_range1, kernel_version_range2) == expected_result
