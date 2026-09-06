import re
from typing import List

import pytest

from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.optfeatures.optfeature import OptFeature
from ebuild_analyzer.optfeatures.optfeatures_extractor import OptFeaturesExtractor
from ebuild_analyzer.package_atoms.package_atom import PackageAtom


def __assert_optfeatures_equal(first: List[OptFeature], second: List[OptFeature]) -> None:
    # The visibility conditions are not really relevant here since they are tested separate in the path conditions
    # analyzer tests more thoroughly.
    assert len(first) == len(second)

    for i in range(len(first)):
        assert first[i].header == second[i].header
        assert first[i].description == second[i].description
        assert first[i].possible_feature_dependencies == second[i].possible_feature_dependencies


@pytest.mark.parametrize("bash, expected_optfeatures", [
    (b"optfeature desc pkg", [OptFeature([], None, "desc", [[PackageAtom("pkg")]])]),
    (b"optfeature desc pkg1 pkg2", [OptFeature([], None, "desc", [[PackageAtom("pkg1")], [PackageAtom("pkg2")]])]),
    (b"optfeature desc 'pkg1 pkg2'", [OptFeature([], None, "desc", [[PackageAtom("pkg1"), PackageAtom("pkg2")]])]),
    (b"optfeature desc 'pkg1 pkg2' pkg3",
     [OptFeature([], None, "desc", [[PackageAtom("pkg1"), PackageAtom("pkg2")], [PackageAtom("pkg3")]])]),
])
def test_package_atom_extraction(bash: bytes, expected_optfeatures: List[OptFeature], bash_parser: BashParser,
                                 optfeatures_extractor: OptFeaturesExtractor):
    optfeature_nodes = bash_parser.parse(bash).get_all_nodes_of_type(NodeType.COMMAND, re.compile("optfeature"))
    __assert_optfeatures_equal(optfeatures_extractor.extract(optfeature_nodes), expected_optfeatures)


@pytest.mark.parametrize("bash, expected_optfeatures", [
    (b"optfeature desc pkg1[use]",
     [OptFeature([], None, "desc", [[PackageAtom("pkg1", required_enabled_use_flags=["use"])]])]),
    (b"optfeature desc pkg1[-use,use2]",
     [OptFeature([], None, "desc",
                 [[PackageAtom("pkg1", required_enabled_use_flags=["use2"], required_disabled_use_flags=["use"])]])]),
])
def test_per_package_use_flags(bash: bytes, expected_optfeatures: List[OptFeature], bash_parser: BashParser,
                               optfeatures_extractor: OptFeaturesExtractor):
    optfeature_nodes = bash_parser.parse(bash).get_all_nodes_of_type(NodeType.COMMAND, re.compile("optfeature"))
    __assert_optfeatures_equal(optfeatures_extractor.extract(optfeature_nodes), expected_optfeatures)


@pytest.mark.parametrize("bash, expected_optfeatures", [
    (b"optfeature desc pkg\n"
     b"optfeature desc2 pkg2",
     [OptFeature([], None, "desc", [[PackageAtom("pkg")]]), OptFeature([], None, "desc2", [[PackageAtom("pkg2")]])]),

    (b"optfeature desc pkg\n"
     b"optfeature desc2 pkg2\n"
     b"optfeature desc3 pkg3",
     [OptFeature([], None, "desc", [[PackageAtom("pkg")]]), OptFeature([], None, "desc2", [[PackageAtom("pkg2")]]),
      OptFeature([], None, "desc3", [[PackageAtom("pkg3")]])]),
])
def test_multiple_optfeatures(bash: bytes, expected_optfeatures: List[OptFeature], bash_parser: BashParser,
                              optfeatures_extractor: OptFeaturesExtractor):
    optfeature_nodes = bash_parser.parse(bash).get_all_nodes_of_type(NodeType.COMMAND, re.compile("optfeature"))
    __assert_optfeatures_equal(optfeatures_extractor.extract(optfeature_nodes), expected_optfeatures)


@pytest.mark.parametrize("bash, expected_optfeatures", [
    (b"optfeature_header\n"
     b"optfeature desc pkg", [OptFeature([], None, "desc", [[PackageAtom("pkg")]])]),

    (b"optfeature_header header\n"
     b"optfeature desc pkg", [OptFeature([], "header", "desc", [[PackageAtom("pkg")]])]),

    (b"optfeature_header header\n"
     b"optfeature desc pkg\n"
     b"optfeature desc2 pkg2",
     [OptFeature([], "header", "desc", [[PackageAtom("pkg")]]),
      OptFeature([], "header", "desc2", [[PackageAtom("pkg2")]])]),

    (b"optfeature_header header\n"
     b"optfeature desc pkg\n"
     b"optfeature_header header2\n"
     b"optfeature desc2 pkg2",
     [OptFeature([], "header", "desc", [[PackageAtom("pkg")]]),
      OptFeature([], "header2", "desc2", [[PackageAtom("pkg2")]])]),

    (b"optfeature_header header\n"
     b"optfeature desc pkg\n"
     b"optfeature desc2 pkg2\n"
     b"optfeature_header header2\n"
     b"optfeature desc3 pkg3",
     [OptFeature([], "header", "desc", [[PackageAtom("pkg")]]),
      OptFeature([], "header", "desc2", [[PackageAtom("pkg2")]]),
      OptFeature([], "header2", "desc3", [[PackageAtom("pkg3")]])]),
])
def test_header_extraction(bash: bytes, expected_optfeatures: List[OptFeature], bash_parser: BashParser,
                           optfeatures_extractor: OptFeaturesExtractor):
    optfeature_nodes = bash_parser.parse(bash).get_all_nodes_of_type(NodeType.COMMAND, re.compile("optfeature"))
    __assert_optfeatures_equal(optfeatures_extractor.extract(optfeature_nodes), expected_optfeatures)
