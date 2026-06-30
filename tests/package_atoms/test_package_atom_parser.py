import pytest

from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.package_atoms.package_atom_parser import PackageAtomParser


@pytest.mark.parametrize("package_atom_text, expected_package_atom", [
    ("atom", PackageAtom("atom", [], [])),
    ("atom[use]", PackageAtom("atom", ["use"], [])),
    ("atom[-use]", PackageAtom("atom", [], ["use"])),
    ("atom[use1,-use2]", PackageAtom("atom", ["use1"], ["use2"])),
    ("atom[-use1,use2]", PackageAtom("atom", ["use2"], ["use1"])),
    ("atom[use1,-use2,use3,-use4]", PackageAtom("atom", ["use1", "use3"], ["use2", "use4"])),
    ("atom[use1(+),use2(-)]", PackageAtom("atom", ["use1"], ["use2"])),
    (">=atom-1232[use]", PackageAtom(">=atom-1232", ["use"], [])),
])
def test_sanity(package_atom_text: str, expected_package_atom: PackageAtom, package_atom_parser: PackageAtomParser):
    assert package_atom_parser.parse(package_atom_text) == expected_package_atom
