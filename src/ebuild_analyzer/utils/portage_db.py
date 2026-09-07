from typing import List, Set

import portage

from ebuild_analyzer.ebuild.ebuild import Ebuild
from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV


class PackageNotFoundException(Exception):
    pass


class PortageDatabase:
    def __init__(self) -> None:
        # noinspection PyUnresolvedReferences
        self.__vardb = portage.db[portage.root]["vartree"].dbapi
        # noinspection PyUnresolvedReferences
        self.__portdb = portage.db[portage.root]["porttree"].dbapi

    def get_best_installed_cpv(self, package_atom: PackageAtom) -> PackageCPV:
        if not self.is_package_installed(package_atom):
            raise PackageNotFoundException(f"Package '{package_atom.text}' not installed: can't get CPV")

        candidate_cpvs = self.__vardb.match(package_atom.text)
        return PackageCPV.from_string(candidate_cpvs[-1])

    def get_best_visible_cpv(self, package_atom: PackageAtom) -> PackageCPV:
        cpv = self.__portdb.xmatch("bestmatch-visible", package_atom.text)
        if not cpv:
            raise PackageNotFoundException(f"No matching visible package for atom {package_atom.text}")
        return PackageCPV.from_string(cpv)

    def get_best_cpv(self, package_atom: PackageAtom) -> PackageCPV:
        cpvs = self.__portdb.xmatch("match-all", package_atom.text)
        if not cpvs:
            raise PackageNotFoundException(f"No matching package for atom {package_atom.text}")
        best_cpv = portage.best(cpvs)
        return PackageCPV.from_string(best_cpv)

    def get_all_packages(self) -> List[PackageCPV]:
        return [PackageCPV.from_string(cpv) for cpv in self.__portdb.cpv_all()]

    def get_all_installed_packages(self) -> List[PackageCPV]:
        return [PackageCPV.from_string(cpv) for cpv in self.__vardb.cpv_all()]

    def get_ebuild(self, package_cpv: PackageCPV) -> Ebuild:
        return Ebuild(package_cpv, self.__get_db(package_cpv.text).findname(package_cpv.text))

    def is_package_installed(self, package_atom: PackageAtom) -> bool:
        return bool(self.__vardb.match(package_atom.text))

    def is_package_masked(self, package_atom: PackageAtom) -> bool:
        return not bool(self.__portdb.xmatch("match-visible", package_atom.text))

    def does_package_exist(self, package_atom: PackageAtom) -> bool:
        return bool(self.__portdb.xmatch("match-all", package_atom.text))

    def is_use_flag_enabled(self, package_cpv: PackageCPV, use_flag: str) -> bool:
        return use_flag in self.get_enabled_use_flags(package_cpv)

    def get_enabled_use_flags(self, package_cpv: PackageCPV) -> Set[str]:
        return set(self.__get_db(package_cpv.text).aux_get(package_cpv.text, ["USE"])[0].split())

    def get_metadata_key(self, package_cpv: PackageCPV, key: str) -> str:
        return self.__get_db(package_cpv.text).aux_get(package_cpv.text, [key])[0]

    def __get_db(self, package_atom_string: str):
        if self.__vardb.cpv_exists(package_atom_string):
            return self.__vardb
        else:
            return self.__portdb
