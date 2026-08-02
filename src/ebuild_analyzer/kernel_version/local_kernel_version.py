import platform
import re
from functools import cache

from ebuild_analyzer.kernel_version.kernel_version import KernelVersion

__KERNEL_VERSION_RE = re.compile(r"(\d+)\.(\d+)(?:\.(\d+))?")


@cache
def get_local_kernel_version() -> KernelVersion:
    release = platform.release()

    match = __KERNEL_VERSION_RE.match(release)
    if match is None:
        raise RuntimeError(f"Could not parse kernel version: {release}")

    major, minor, patch = match.groups(default="0")
    return KernelVersion(int(major), int(minor), int(patch))
