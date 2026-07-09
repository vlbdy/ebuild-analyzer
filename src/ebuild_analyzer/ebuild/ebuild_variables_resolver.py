from typing import Dict

from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.utils.portage_db import PortageDatabase


class EbuildVariablesResolver:
    def __init__(self, portage_db: PortageDatabase) -> None:
        self.__portage_db = portage_db

    def resolve_all(self, package_cpv: PackageCPV) -> Dict[str, str]:
        all_variables = self.resolve_default_variables(package_cpv)
        all_variables.update(self.resolve_metadata_variables(package_cpv))
        return all_variables

    def resolve_metadata_variables(self, package_cpv: PackageCPV) -> Dict[str, str]:
        # These are metadata variables which were used somewhere in an optfeature
        metadata_keys = ("SLOT",)
        metadata_variables: Dict[str, str] = dict()

        for key in metadata_keys:
            metadata_variables[key] = self.__portage_db.get_metadata_key(package_cpv, key)
        return metadata_variables

    @staticmethod
    def resolve_default_variables(package_cpv: PackageCPV) -> Dict[str, str]:
        category = package_cpv.category
        package_name = package_cpv.package
        package_version = package_cpv.version
        package_revision = package_cpv.revision

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
