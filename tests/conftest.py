import pytest

from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.package_atoms.package_atom_normalizer import PackageAtomNormalizer
from ebuild_analyzer.package_atoms.package_atom_parser import PackageAtomParser


@pytest.fixture(scope='session')
def bash_parser() -> BashParser:
    return BashParser()


@pytest.fixture(scope='session')
def package_atom_parser() -> PackageAtomParser:
    return PackageAtomParser()


@pytest.fixture(scope='session')
def package_atom_normalizer() -> PackageAtomNormalizer:
    return PackageAtomNormalizer()
