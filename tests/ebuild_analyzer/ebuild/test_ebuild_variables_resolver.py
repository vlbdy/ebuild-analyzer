from typing import Dict

import pytest

from ebuild_analyzer.ebuild.ebuild_variables_resolver import EbuildVariablesResolver
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV


@pytest.mark.parametrize("package_cpv, expected_variables", [
    (
            PackageCPV.from_string("dev-lang/rust-bin-1.95.0"),
            {
                "P": "rust-bin-1.95.0",
                "PN": "rust-bin",
                "PV": "1.95.0",
                "PR": "r0",
                "PVR": "1.95.0-r0",
                "PF": "rust-bin-1.95.0",
                "CATEGORY": "dev-lang",
            }
    ),
    (
            PackageCPV.from_string("dev-lang/rust-bin-1.95.0-r10"),
            {
                "P": "rust-bin-1.95.0",
                "PN": "rust-bin",
                "PV": "1.95.0",
                "PR": "r10",
                "PVR": "1.95.0-r10",
                "PF": "rust-bin-1.95.0-r10",
                "CATEGORY": "dev-lang",
            }
    ),
])
def test_default_variables_resolution_sanity(package_cpv: PackageCPV, expected_variables: Dict[str, str]):
    assert EbuildVariablesResolver.resolve_default_variables(package_cpv) == expected_variables
