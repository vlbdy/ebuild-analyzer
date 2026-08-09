from typing import Set

from ebuild_analyzer.kernel_config.local.kernel_config_key import KernelConfigKey, KernelConfigState


class LocalKernelConfig:
    def __init__(self, local_config_keys: Set[KernelConfigKey]):
        self.__local_config_keys = local_config_keys

    def is_set(self, key: str) -> bool:
        for local_key in self.__local_config_keys:
            if local_key.name == key and local_key.value != KernelConfigState.DISABLED:
                return True
        return False

    def get_all_keys(self) -> Set[KernelConfigKey]:
        return self.__local_config_keys.copy()
