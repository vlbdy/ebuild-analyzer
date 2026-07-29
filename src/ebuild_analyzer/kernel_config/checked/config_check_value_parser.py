from ebuild_analyzer.kernel_config.checked.checked_kernel_config_key import CheckedKernelConfigKey


class ConfigCheckValueParser:
    def parse(self, config_check_kernel_config_key: str) -> CheckedKernelConfigKey:
        required = True
        enabled = True

        while not config_check_kernel_config_key[0].isalpha():
            if config_check_kernel_config_key[0] == '~':
                required = False
            elif config_check_kernel_config_key[0] == '!':
                enabled = False
            config_check_kernel_config_key = config_check_kernel_config_key[1:]

        return CheckedKernelConfigKey(config_check_kernel_config_key, enabled, required)
