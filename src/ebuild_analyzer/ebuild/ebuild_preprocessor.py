import re

from ebuild_analyzer.ebuild.ebuild_variables_resolver import EbuildVariablesResolver
from ebuild_analyzer.ebuild.preprocessed_ebuild import PreprocessedEbuild
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.ebuild.ebuild import Ebuild


class EbuildPreprocessor:
    def __init__(self, ebuild_variables_resolver: EbuildVariablesResolver) -> None:
        self.__ebuild_variables_resolver = ebuild_variables_resolver

    def preprocess(self, ebuild: Ebuild) -> PreprocessedEbuild:
        preprocessed_contents = ebuild.contents
        preprocessed_contents = self.__join_line_continuations(preprocessed_contents)
        preprocessed_contents = self.__expand_variables(ebuild.cpv, preprocessed_contents)
        return PreprocessedEbuild(ebuild.cpv, ebuild.path, preprocessed_contents)

    def __join_line_continuations(self, ebuild_contents: bytes) -> bytes:
        return re.sub(rb'\\\n\s*', b'', ebuild_contents)

    def __expand_variables(self, package_cpv: PackageCPV, ebuild_contents: bytes) -> bytes:
        variables = self.__ebuild_variables_resolver.resolve_all(package_cpv)

        for key, value in variables.items():
            # Replaces all instances of `${key}` with `value`
            ebuild_contents = ebuild_contents.replace(f"${{{key}}}".encode(), value.encode())
        return ebuild_contents
