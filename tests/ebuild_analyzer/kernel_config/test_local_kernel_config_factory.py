from ebuild_analyzer.kernel_config.local.kernel_config_key import KernelConfigKey, KernelConfigState
from ebuild_analyzer.kernel_config.local.local_kernel_config_factory import LocalKernelConfigFactory


def test_sanity(local_kernel_config_factory: LocalKernelConfigFactory):
    lines = ["CONFIG_BUILT_IN=y", "CONFIG_MODULE=m", "# CONFIG_UNSET is not set", "#", "# Something random"]

    local_kernel_config = local_kernel_config_factory.from_lines(lines)

    assert local_kernel_config.get_all_keys() == {
        KernelConfigKey("BUILT_IN", KernelConfigState.BUILT_IN),
        KernelConfigKey("MODULE", KernelConfigState.MODULE),
        KernelConfigKey("UNSET", KernelConfigState.DISABLED),
    }
