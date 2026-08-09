import pytest

from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.kernel_config.local.kernel_config_entry_parser import KernelConfigEntryParser
from ebuild_analyzer.kernel_config.local.local_kernel_config_factory import LocalKernelConfigFactory
from ebuild_analyzer.optfeatures.optfeatures_extractor import OptFeaturesExtractor
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


@pytest.fixture(scope='session')
def optfeatures_extractor() -> OptFeaturesExtractor:
    return OptFeaturesExtractor()


@pytest.fixture(scope='session')
def kernel_config_entry_parser() -> KernelConfigEntryParser:
    return KernelConfigEntryParser()


@pytest.fixture(scope='session')
def local_kernel_config_factory() -> LocalKernelConfigFactory:
    return LocalKernelConfigFactory()
