from typing import List

import pytest

from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.path_conditions.command_interpreters.has_version_command_interpreter import \
    HasVersionCommandInterpreter
from ebuild_analyzer.path_conditions.path_condition import PathCondition


@pytest.mark.parametrize("arguments, expected_path_condition", [
    (["package"], PathCondition(installed_packages={PackageAtom("package")})),
    (["-b", "package"], PathCondition(installed_packages={PackageAtom("package")})),
    (["=category/package"], PathCondition(installed_packages={PackageAtom("=category/package")})),
    (["=category/package-1.2.3"], PathCondition(installed_packages={PackageAtom("=category/package-1.2.3")})),
    (["=category/package-1.2.3[use1]"],
     PathCondition(installed_packages={PackageAtom("=category/package-1.2.3", required_enabled_use_flags=["use1"])})),
])
def test_sanity(arguments: List[str], expected_path_condition: PathCondition):
    assert HasVersionCommandInterpreter().create_path_conditions(arguments) == expected_path_condition
