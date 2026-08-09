import gzip
from typing import List

from ebuild_analyzer.kernel_config.local.kernel_config_entry_parser import KernelConfigEntryParser
from ebuild_analyzer.kernel_config.local.local_kernel_config import LocalKernelConfig


class LocalKernelConfigFactory:
    __DEFAULT_CONFIG_GZ_PATH = "/proc/config.gz"

    def __init__(self):
        self.__kernel_config_entry_parser = KernelConfigEntryParser()

    def from_running_kernel(self) -> LocalKernelConfig:
        with gzip.open(self.__DEFAULT_CONFIG_GZ_PATH, "rt") as kernel_config_file:
            return self.from_lines(kernel_config_file.readlines())

    def from_file(self, file: str) -> LocalKernelConfig:
        with open(file, "r") as kernel_config_file:
            return self.from_lines(kernel_config_file.readlines())

    def from_lines(self, entry_lines: List[str]) -> LocalKernelConfig:
        kernel_config_keys = set()
        for entry_line in entry_lines:
            if "CONFIG_" in entry_line:
                print(entry_line)
                kernel_config_keys.add(self.__kernel_config_entry_parser.parse(entry_line))
        return LocalKernelConfig(kernel_config_keys)
