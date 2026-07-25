from typing import List

import pytest

from ebuild_analyzer.kernel_version.kernel_version import KernelVersion
from ebuild_analyzer.kernel_version.kernel_version_range import KernelVersionRange
from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.path_conditions.path_condition import PathCondition


def test_iadd():
    pc = PathCondition(
        enabled_use_flags={'a'},
        disabled_use_flags={'b'},
    )

    pc += PathCondition(
        enabled_use_flags={'c'},
        installed_packages={PackageAtom("atom")}
    )

    assert pc == PathCondition(
        enabled_use_flags={'a', 'c'},
        disabled_use_flags={'b'},
        installed_packages={PackageAtom("atom")}
    )


def test_add():
    pc = PathCondition(
        enabled_use_flags={'a'},
        disabled_use_flags={'b'},
    )

    pc2 = PathCondition(
        enabled_use_flags={'c'},
        installed_packages={PackageAtom("atom")}
    )

    new_pc = pc + pc2

    assert pc == PathCondition(
        enabled_use_flags={'a'},
        disabled_use_flags={'b'},
    )
    assert pc2 == PathCondition(
        enabled_use_flags={'c'},
        installed_packages={PackageAtom("atom")}
    )
    assert new_pc == PathCondition(
        enabled_use_flags={'a', 'c'},
        disabled_use_flags={'b'},
        installed_packages={PackageAtom("atom")}
    )


def test_bool():
    assert bool(PathCondition()) == False
    assert bool(PathCondition(disabled_use_flags={'a'})) == True


@pytest.mark.parametrize("path_condition1, path_condition2, expected_path_conditions", [
    (PathCondition(enabled_use_flags={'a'}, disabled_use_flags={'b'}),
     PathCondition(enabled_use_flags={'c'}, installed_packages={PackageAtom("atom")}),
     [PathCondition(enabled_use_flags={'a'}, disabled_use_flags={'b', 'c'},
                    uninstalled_packages={PackageAtom("atom")})]),
    (PathCondition(),
     PathCondition(kernel_version_range=KernelVersionRange.between(KernelVersion(1), KernelVersion(3))),
     [PathCondition(kernel_version_range=KernelVersionRange.less_than(KernelVersion(1))),
      PathCondition(kernel_version_range=KernelVersionRange.at_least(KernelVersion(3)))]),

    (PathCondition(kernel_version_range=KernelVersionRange.between(KernelVersion(3), KernelVersion(7))),
     PathCondition(kernel_version_range=KernelVersionRange.at_most(KernelVersion(5))),
     [PathCondition(kernel_version_range=KernelVersionRange.between(KernelVersion(5), KernelVersion(7),
                                                                    min_inclusive=False, max_inclusive=False))])
])
def test_and_not(path_condition1: PathCondition, path_condition2: PathCondition,
                 expected_path_conditions: List[PathCondition]):
    assert path_condition1.and_not(path_condition2) == expected_path_conditions


@pytest.mark.parametrize("path_condition, expected_path_conditions", [
    (
            PathCondition(enabled_use_flags={'a'}, disabled_use_flags={'b'}, installed_packages={PackageAtom("atom1")},
                          uninstalled_packages={PackageAtom("atom2")},
                          kernel_version_range=KernelVersionRange.between(KernelVersion(1), KernelVersion(2))),
            [
                PathCondition(disabled_use_flags={'a'}),
                PathCondition(enabled_use_flags={'b'}),
                PathCondition(uninstalled_packages={PackageAtom("atom1")}),
                PathCondition(installed_packages={PackageAtom("atom2")}),
                PathCondition(kernel_version_range=KernelVersionRange.less_than(KernelVersion(1))),
                PathCondition(kernel_version_range=KernelVersionRange.at_least(KernelVersion(2))),
            ]
    )
])
def test_negate(path_condition: PathCondition, expected_path_conditions: List[PathCondition]):
    negated_path_conditions = path_condition.negate()

    assert len(negated_path_conditions) == len(expected_path_conditions)
    for negated_pc in negated_path_conditions:
        assert negated_pc in expected_path_conditions
