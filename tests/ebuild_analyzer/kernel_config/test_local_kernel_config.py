import pytest

from ebuild_analyzer.kernel_config.local.kernel_config_key import KernelConfigKey
from ebuild_analyzer.kernel_config.local.local_kernel_config import LocalKernelConfig


@pytest.fixture(scope='module')
def local_kernel_config() -> LocalKernelConfig:
    return LocalKernelConfig({
        KernelConfigKey("TEST_BUILT_IN", "y"),
        KernelConfigKey("TEST_MODULE", "m"),
        KernelConfigKey("TEST_DISABLED", "n"),
        KernelConfigKey("TEST_STRING", "string"),
    })


@pytest.mark.parametrize("config_key, expected_result", [
    ("TEST_BUILT_IN", True),
    ("TEST_MODULE", True),
    ("TEST_DISABLED", False),
    ("TEST_STRING", True),
])
def test_is_set(local_kernel_config: LocalKernelConfig, config_key: str, expected_result: bool):
    assert local_kernel_config.is_set(config_key) == expected_result
