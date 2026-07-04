from typing import List

import portage

from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.package_atoms.package_atom_parser import PackageAtomParser
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.utils.package_state_provider import PackageStateProvider


class AmbiguousPackageException(Exception):
    pass


class PackageNotFoundException(Exception):
    pass


class PortageDatabase(PackageStateProvider):
    def __init__(self) -> None:
        # noinspection PyUnresolvedReferences
        self.__db = portage.db[portage.root]["vartree"].dbapi
        self.__package_atom_parser = PackageAtomParser()

    def get_cpv_for_atom(self, package_atom: PackageAtom) -> PackageCPV:
        candidate_cpvs = self.__db.match(package_atom.text)
        if len(candidate_cpvs) > 1:
            raise AmbiguousPackageException(
                f"Ambiguous package '{package_atom.text}', candidates are: {candidate_cpvs}")
        elif not candidate_cpvs:
            raise PackageNotFoundException(f"Package '{package_atom.text}' not found")
        return PackageCPV.from_string(candidate_cpvs[0])

    def get_all_packages(self) -> List[PackageCPV]:
        return [PackageCPV.from_string(cpv) for cpv in self.__db.cpv_all()]

    def get_ebuild_path_for_package(self, package_cpv: PackageCPV) -> str:
        return self.__db.findname(package_cpv.text)

    def is_package_installed(self, package_atom: PackageAtom) -> bool:
        return bool(self.__db.match(package_atom.text))

    def is_use_flag_enabled(self, package_atom: PackageAtom, use_flag: str) -> bool:
        if not self.is_package_installed(package_atom):
            return False

        package_cpv = self.get_cpv_for_atom(package_atom)
        use_flags = set(self.__db.aux_get(package_cpv.text, ["USE"])[0].split())
        return use_flag in use_flags

    def get_metadata_key(self, package_cpv: PackageCPV, key: str) -> str:
        return self.__db.aux_get(package_cpv.text, [key])[0]
