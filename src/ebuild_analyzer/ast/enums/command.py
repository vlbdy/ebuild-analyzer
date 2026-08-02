from enum import StrEnum


class Command(StrEnum):
    USE = "use"
    HAS_VERSION = "has_version"
    OPTFEATURE = "optfeature"
    OPTFEATURE_HEADER = "optfeature_header"
    KERNEL_IS = "kernel_is"
    LINUX_CONFIG_EXISTS = "linux_config_exists"
    LINUX_INFO_PKG_SETUP = "linux-info_pkg_setup"
    CHECK_EXTRA_CONFIG = "check_extra_config"
