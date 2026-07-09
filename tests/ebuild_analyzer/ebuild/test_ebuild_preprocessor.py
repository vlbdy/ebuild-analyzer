from dataclasses import dataclass
from typing import Dict

import pytest

from ebuild_analyzer.ebuild.ebuild import Ebuild
from ebuild_analyzer.ebuild.ebuild_preprocessor import EbuildPreprocessor
from ebuild_analyzer.ebuild.ebuild_variables_resolver import EbuildVariablesResolver
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV


class MockEbuildVariablesResolver(EbuildVariablesResolver):
    def resolve_all(self, package_cpv: PackageCPV) -> Dict[str, str]:
        # Metadata variables are not relevant for these tests
        return EbuildVariablesResolver.resolve_default_variables(package_cpv)


@dataclass(frozen=True)
class MockEbuild(Ebuild):
    _contents: bytes

    @property
    def contents(self) -> bytes:
        return self._contents

    @classmethod
    def with_contents(cls, contents: bytes) -> MockEbuild:
        return MockEbuild(PackageCPV.from_string("www-client/firefox-bin-152.0.1"), "/", contents)


@pytest.fixture(scope='module')
def ebuild_preprocessor() -> EbuildPreprocessor:
    # The mocked resolver implementation does not use the database field
    return EbuildPreprocessor(MockEbuildVariablesResolver(None))


@pytest.mark.parametrize("ebuild, expected_preprocessed_contents", [
    (MockEbuild.with_contents(b"line continu\\\nation"), b"line continuation"),
    (MockEbuild.with_contents(b"lin\\\ne c\\\n  ontinu\\\nation"), b"line continuation"),
    (MockEbuild.with_contents(b"line continu\\\n         ation"), b"line continuation"),
    (MockEbuild.with_contents(b"${CATEGORY} test ${PF} test ${UNKNOWN}"),
     b"www-client test firefox-bin-152.0.1 test ${UNKNOWN}"),
])
def test_sanity(ebuild_preprocessor: EbuildPreprocessor, ebuild: MockEbuild, expected_preprocessed_contents: bytes):
    assert ebuild_preprocessor.preprocess(ebuild).contents == expected_preprocessed_contents
