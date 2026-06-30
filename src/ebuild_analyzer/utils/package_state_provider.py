from typing import Protocol


class PackageStateProvider(Protocol):
    def is_package_installed(self, package: str) -> bool: ...

    def is_use_flag_enabled(self, package: str, use_flag: str) -> bool: ...
