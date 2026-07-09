from typing import Protocol

from ebuild_analyzer.ebuild.ebuild import Ebuild
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV


class CommandHandler(Protocol):
    def handle(self, package_cpv: PackageCPV, ebuild: Ebuild) -> None: ...
