from typing import Protocol

from ebuild_analyzer.package_atoms.package_atom import PackageAtom


class PackageStateProvider(Protocol):
    def is_package_installed(self, package_atom: PackageAtom) -> bool: ...

    def is_use_flag_enabled(self, package_atom: PackageAtom, use_flag: str) -> bool: ...
