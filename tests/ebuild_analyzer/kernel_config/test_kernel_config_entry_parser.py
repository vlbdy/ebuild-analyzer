import pytest

from ebuild_analyzer.kernel_config.local.kernel_config_entry_parser import KernelConfigEntryParser
from ebuild_analyzer.kernel_config.local.kernel_config_key import KernelConfigKey


@pytest.mark.parametrize("entry, expected_parsed_entry", [
    ("CONFIG_TEST=y", KernelConfigKey("TEST", "y")),
    ("CONFIG_TEST=m", KernelConfigKey("TEST", "m")),
    ("# CONFIG_TEST is not set", KernelConfigKey("TEST", "n")),
    ('CONFIG_TEST="this is a string="', KernelConfigKey("TEST", "this is a string=")),
    ('CONFIG_TEST=""', KernelConfigKey("TEST", "")),
])
def test_sanity(kernel_config_entry_parser: KernelConfigEntryParser, entry: str,
                expected_parsed_entry: KernelConfigKey):
    assert kernel_config_entry_parser.parse(entry) == expected_parsed_entry
