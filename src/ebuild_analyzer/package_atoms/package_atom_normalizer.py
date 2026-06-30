class PackageAtomNormalizer:
    def normalize(self, package_atom: str) -> str:
        package_atom = self.__remove_variables_from_package_string(package_atom)
        package_atom = self.__remove_invalid_characters_from_package_string(package_atom)
        return package_atom

    def __remove_variables_from_package_string(self, package_string: str) -> str:
        # This parser does not fully support variable expansion, so unexpanded variables are removed to ensure
        # that the ebuild analyzer can still work.
        if '$' not in package_string:
            return package_string
        return package_string[:package_string.index('$')]

    def __remove_invalid_characters_from_package_string(self, package_string: str) -> str:
        # Usually after removing a variable from the end of a package string, the last character will be ':'
        # so it should be removed
        if package_string.endswith(':'):
            return package_string[:-1]
        return package_string
