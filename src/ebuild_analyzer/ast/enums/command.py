from enum import StrEnum


class Command(StrEnum):
    USE = "use"
    HAS_VERSION = "has_version"
    OPTFEATURE = "optfeature"
    OPTFEATURE_HEADER = "optfeature_header"
    KERNEL_IS = "kernel_is"
