from dataclasses import dataclass

from ebuild_analyzer.ebuild.ebuild import Ebuild


@dataclass(frozen=True)
class PreprocessedEbuild(Ebuild):
    _contents: bytes

    @property
    def contents(self) -> bytes:
        return self._contents
