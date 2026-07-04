import re
from typing import Dict

from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.utils.portage_db import PortageDatabase


class Ebuild:
    def __init__(self, package_cpv: PackageCPV, portage_db: PortageDatabase, path: str) -> None:
        self.__package_cpv = package_cpv
        self.__portage_db = portage_db
        self.__path = path

    def get_normalized_contents(self) -> bytes:
        with open(self.__path, "rb") as ebuild_file:
            ebuild_contents = ebuild_file.read()
            ebuild_contents = self.__join_line_continuations(ebuild_contents)
            ebuild_contents = self.__expand_variables(ebuild_contents)
            return ebuild_contents

    def __join_line_continuations(self, ebuild_contents: bytes) -> bytes:
        return re.sub(rb'\\\n\s*', b'', ebuild_contents)

    def __expand_variables(self, ebuild_contents: bytes) -> bytes:
        variables = self.__get_all_variables()

        for key, value in variables.items():
            # Replaces all instances of `${key}` with `value`
            ebuild_contents = ebuild_contents.replace(f"${{{key}}}".encode(), value.encode())
        return ebuild_contents

    def __get_all_variables(self) -> Dict[str, str]:
        all_variables = self.__get_default_variables()
        all_variables.update(self.__get_metadata_variables())
        return all_variables

    def __get_metadata_variables(self) -> Dict[str, str]:
        # These are metadata variables which were used somewhere in an optfeature
        metadata_keys = ("SLOT",)
        metadata_variables: Dict[str, str] = dict()

        for key in metadata_keys:
            metadata_variables[key] = self.__portage_db.get_metadata_key(self.__package_cpv, key)
        return metadata_variables

    def __get_default_variables(self) -> Dict[str, str]:
        category = self.__package_cpv.category
        package_name = self.__package_cpv.package
        package_version = self.__package_cpv.version
        package_revision = self.__package_cpv.revision

        # r0 revisions are omitted in the PF variable
        if package_revision == "r0":
            full_package = f"{package_name}-{package_version}"
        else:
            full_package = f"{package_name}-{package_version}-{package_revision}"

        return {
            "P": f"{package_name}-{package_version}",
            "PN": package_name,
            "PV": package_version,
            "PR": package_revision,
            "PVR": f"{package_version}-{package_revision}",
            "PF": full_package,
            "CATEGORY": category,
        }
