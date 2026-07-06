from typing import List

import pytest

from ebuild_analyzer.optfeatures.optfeature import OptFeature
from ebuild_analyzer.optfeatures.optfeature_availability_checker import OptFeatureAvailabilityChecker
from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.utils.portage_db import PortageDatabase


class MockPortageDatabase(PortageDatabase):
    def is_package_installed(self, package_atom: PackageAtom) -> bool:
        return package_atom.text.startswith("installed")

    def is_use_flag_enabled(self, package_cpv: PackageCPV, use_flag: str) -> bool:
        return use_flag.startswith("enabled")

    def get_best_installed_cpv(self, package_atom: PackageAtom) -> PackageCPV:
        return PackageCPV.from_string("mock/pkg-1.0.0")


@pytest.fixture(scope="module")
def optfeature_availability_checker() -> OptFeatureAvailabilityChecker:
    return OptFeatureAvailabilityChecker(MockPortageDatabase())


@pytest.mark.parametrize("possible_dependencies, expected_result", [
    ([[PackageAtom("installed", [], [])]], True),
    ([[PackageAtom("not", [], [])]], False),

    ([[PackageAtom("installed", ["enabled"], [])]], True),
    ([[PackageAtom("installed", ["not"], [])]], False),
    ([[PackageAtom("installed", [], ["enabled"])]], False),
    ([[PackageAtom("installed", [], ["not"])]], True),

    ([[PackageAtom("installed", ["enabled"], ["not"])]], True),
    ([[PackageAtom("installed", ["enabled"], ["enabled"])]], False),
    ([[PackageAtom("installed", ["not"], ["enabled"])]], False),
    ([[PackageAtom("installed", ["not"], ["not"])]], False),

    ([[PackageAtom("installed", [], [])], [PackageAtom("installed", [], [])]], True),
    ([[PackageAtom("installed", [], [])], [PackageAtom("not", [], [])]], True),
    ([[PackageAtom("not", [], [])], [PackageAtom("installed", [], [])]], True),

    ([[PackageAtom("installed", ["enabled"], [])], [PackageAtom("installed", ["not"], [])]], True),

    ([[PackageAtom("installed", [], []), PackageAtom("not", [], [])]], False),
    ([[PackageAtom("installed", [], []), PackageAtom("installed", [], [])]], True),
    ([[PackageAtom("installed", ["enabled"], []), PackageAtom("installed", ["enabled"], [])]], True),
    ([[PackageAtom("installed", ["enabled"], []), PackageAtom("installed", ["not"], [])]], False),
])
def test_sanity(possible_dependencies: List[List[PackageAtom]], expected_result: bool,
                optfeature_availability_checker: OptFeatureAvailabilityChecker):
    optfeature = __create_optfeature(possible_dependencies)
    assert optfeature_availability_checker.is_available(optfeature) == expected_result


def __create_optfeature(possible_dependencies: List[List[PackageAtom]]) -> OptFeature:
    return OptFeature([], None, "", possible_dependencies)
