from dataclasses import dataclass
from typing import Dict

import pytest

from ebuild_analyzer.ebuild.ebuild import Ebuild
from ebuild_analyzer.ebuild.ebuild_preprocessor import EbuildPreprocessor
from ebuild_analyzer.ebuild.ebuild_variables_resolver import EbuildVariablesResolver
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV


class MockEbuildVariablesResolver(EbuildVariablesResolver):
    def resolve_all(self, package_cpv: PackageCPV, ebuild_contents: bytes) -> Dict[str, str]:
        # Metadata variables are not relevant for these tests
        variables = EbuildVariablesResolver.resolve_default_variables(package_cpv)
        variables.update(EbuildVariablesResolver.resolve_bash_variables(ebuild_contents))
        return variables


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
    (MockEbuild.with_contents(b'MY_VAR="asdfg" MY_VAR2=53 $MY_VAR ${MY_VAR2}'), b'MY_VAR="asdfg" MY_VAR2=53 asdfg 53'),
    (MockEbuild.with_contents(b'MY_VAR=42 MY_VAR_AGAIN=$MY_VAR $MY_VAR $MY_VAR_AGAIN'),
     b'MY_VAR=42 MY_VAR_AGAIN=42 42 42'),
    (MockEbuild.with_contents(b'MY_VAR=42 MY_VAR_AGAIN="${MY_VAR}AAAA" $MY_VAR $MY_VAR_AGAIN'),
     b'MY_VAR=42 MY_VAR_AGAIN="42AAAA" 42 42AAAA'),
    (MockEbuild.with_contents(b'MY_VAR="a" MY_VAR="${MY_VAR} b" $MY_VAR'), b'MY_VAR="a" MY_VAR="a b" a b')
])
def test_sanity(ebuild_preprocessor: EbuildPreprocessor, ebuild: MockEbuild, expected_preprocessed_contents: bytes):
    assert ebuild_preprocessor.preprocess(ebuild).contents == expected_preprocessed_contents
