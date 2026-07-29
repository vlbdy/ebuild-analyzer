import re


class ConfigCheckValueNormalizer:
    def normalize(self, config_check_value: str) -> str:
        # CONFIG_CHECK variables are irrelevant.
        config_check_value = config_check_value.replace("${CONFIG_CHECK}", '')
        # Other variables are removed to ensure that the code doesn't break, although these cases should be fixed.
        config_check_value = re.sub(r"[!~]*\$\{[^}]*}", "", config_check_value)
        # Remove all the extra spaces everywhere
        config_check_value = ' '.join(config_check_value.split())
        return config_check_value
