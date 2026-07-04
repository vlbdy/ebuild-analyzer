from dataclasses import dataclass

import portage.versions


@dataclass(frozen=True)
class PackageCPV:
    text: str

    category: str
    package: str
    version: str
    revision: str

    @classmethod
    def from_string(cls, package_cpv_string: str) -> PackageCPV:
        return cls(package_cpv_string, *portage.versions.catpkgsplit(package_cpv_string))
