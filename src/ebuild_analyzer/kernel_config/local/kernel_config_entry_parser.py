from ebuild_analyzer.kernel_config.local.kernel_config_key import KernelConfigKey, KernelConfigState


class KernelConfigEntryParser:
    def parse(self, kernel_config_entry: str) -> KernelConfigKey:
        if self.__is_config_unset(kernel_config_entry):
            key = kernel_config_entry.split(' ')[1]  # This extract the full key name
            key = key.replace("CONFIG_", "")
            return KernelConfigKey(key, KernelConfigState.DISABLED.value)
        else:
            key, value = kernel_config_entry.split('=', 1)
            key = key.replace("CONFIG_", "")

            value = value.strip()
            if self.__is_string_value(value):
                value = value[1:-1]  # Strip the "

            return KernelConfigKey(key, value)

    def __is_config_unset(self, kernel_config_key: str) -> bool:
        return kernel_config_key.startswith('#')

    def __is_string_value(self, value: str) -> bool:
        return value.startswith('"')
