import pytest

from ebuild_analyzer.package_atoms.package_atom_normalizer import PackageAtomNormalizer


@pytest.mark.parametrize("package_atom, normalized_package_atom", [
    ("category/package", "category/package"),
    ("category/package:${VAR}", "category/package"),
    ("category/package${VAR}:${VAR}", "category/package"),
])
def test_sanity(package_atom: str, normalized_package_atom: str, package_atom_normalizer: PackageAtomNormalizer):
    assert package_atom_normalizer.normalize(package_atom) == normalized_package_atom
