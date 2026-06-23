from typing import List

import portage


class PortageDatabase:
    def __init__(self) -> None:
        self.__db = portage.db[portage.root]["vartree"].dbapi

    def get_all_packages(self) -> List[str]:
        return self.__db.cpv_all()

    def get_ebuild_path_for_package(self, package: str) -> str:
        return self.__db.findname(self.__get_cpv_for_package(package))

    def is_package_installed(self, package: str) -> bool:
        return bool(self.__db.match(package))

    def is_use_flag_enabled(self, package: str, use_flag: str) -> bool:
        if not self.is_package_installed(package):
            return False

        cpv = self.__get_cpv_for_package(package)
        use_flags = set(self.__db.aux_get(cpv, ["USE"])[0].split())
        return use_flag in use_flags

    def __get_cpv_for_package(self, package: str) -> str:
        candidate_cpvs = self.__db.match(package)
        if len(candidate_cpvs) > 1:
            raise RuntimeError(f"Ambiguous package '{package}', candidates are: {candidate_cpvs}")
        elif not candidate_cpvs:
            raise RuntimeError(f"Package '{package}' not found")
        return candidate_cpvs[0]
