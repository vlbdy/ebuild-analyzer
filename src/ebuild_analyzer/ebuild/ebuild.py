from dataclasses import dataclass

from ebuild_analyzer.package_atoms.package_cpv import PackageCPV


@dataclass(frozen=True)
class Ebuild:
    cpv: PackageCPV
    path: str

    @property
    def contents(self) -> bytes:
        with open(self.path, "rb") as ebuild_file:
            return ebuild_file.read()
