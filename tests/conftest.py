import pytest

from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.package_atoms.package_atom_normalizer import PackageAtomNormalizer
from ebuild_analyzer.package_atoms.package_atom_parser import PackageAtomParser
from ebuild_analyzer.path_conditions.path_conditions_analyzer import PathConditionsAnalyzer


@pytest.fixture(scope='session')
def bash_parser() -> BashParser:
    return BashParser()


@pytest.fixture(scope='session')
def package_atom_parser() -> PackageAtomParser:
    return PackageAtomParser()


@pytest.fixture(scope='session')
def package_atom_normalizer() -> PackageAtomNormalizer:
    return PackageAtomNormalizer()


@pytest.fixture(scope='session')
def path_conditions_analyzer() -> PathConditionsAnalyzer:
    return PathConditionsAnalyzer()
