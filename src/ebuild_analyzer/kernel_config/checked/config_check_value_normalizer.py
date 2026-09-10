import re


class ConfigCheckValueNormalizer:
    def normalize(self, config_check_value: str) -> str:
        # All variables and commands are removed to ensure that the code doesn't break,
        # although these cases should be fixed.
        config_check_value = re.sub(r"[!~]*\$\{[^}]*}", "", config_check_value)  # ${VAR}
        config_check_value = re.sub(r"[!~]*\$\([^)]*\)", "", config_check_value)  # $(VAR)
        config_check_value = re.sub(r"[!~]*\$[a-zA-Z0-9_]*(?:\s|$)", "", config_check_value)  # $VAR
        # Remove all the extra spaces everywhere
        config_check_value = ' '.join(config_check_value.split())
        return config_check_value
