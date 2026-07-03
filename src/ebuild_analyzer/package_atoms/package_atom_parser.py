import re
from typing import List, Tuple

from ebuild_analyzer.package_atoms.package_atom import PackageAtom


class PackageAtomParser:
    def parse(self, package_string: str) -> PackageAtom:
        # Package atoms can have USE flag requirements listed next to them within square brackets
        if '[' not in package_string:
            return PackageAtom(package_string)

        start = package_string.index("[")
        end = package_string.index("]", start)

        package_name = package_string[:start]
        use_flags = package_string[start + 1:end].split(",")

        required_enabled_use_flags, required_disabled_use_flags = self.__determine_use_flag_categories(use_flags)

        return PackageAtom(package_name, required_enabled_use_flags, required_disabled_use_flags)

    def __determine_use_flag_categories(self, use_flags: List[str]) -> Tuple[List[str], List[str]]:
        required_enabled_use_flags = []
        required_disabled_use_flags = []
        for use_flag in use_flags:
            if match := re.match(r"-(.+)", use_flag):
                required_disabled_use_flags.append(match.group(1))
            elif match := re.match(r"(.+)\(-\)", use_flag):
                required_disabled_use_flags.append(match.group(1))
            elif match := re.match(r"(.+)\(\+\)", use_flag):
                required_enabled_use_flags.append(match.group(1))
            else:
                required_enabled_use_flags.append(use_flag)

        return required_enabled_use_flags, required_disabled_use_flags
