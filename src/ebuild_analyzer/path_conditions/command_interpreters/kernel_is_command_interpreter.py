from typing import List

from ebuild_analyzer.kernel_version.kernel_version import KernelVersion
from ebuild_analyzer.kernel_version.kernel_version_range import KernelVersionRange
from ebuild_analyzer.path_conditions.command_interpreters.command_interpreter import CommandInterpreter
from ebuild_analyzer.path_conditions.path_condition import PathCondition


class KernelIsCommandInterpreter(CommandInterpreter):
    def create_path_conditions(self, arguments: List[str]) -> PathCondition:
        # If the first argument is a digit, it means that no operator was specified
        if arguments[0].isdigit():
            operator = "eq"  # This is the default if no operator was specified
            kernel_version_parts = arguments[0:]
        else:
            operator = arguments[0]
            kernel_version_parts = arguments[1:]

        # Some ebuilds pass the kernel version with periods between the parts, for example '6.11.3' instead of '6 11 3'
        if '.' in kernel_version_parts[0]:
            kernel_version_parts = kernel_version_parts[0].split('.')

        # This line pads the kernel version parts with `None` if there aren't at least 3 parts
        major, minor, patch = (kernel_version_parts + [0] * 3)[:3]
        kernel_version = KernelVersion(major, minor, patch)

        match operator:
            case "-lt" | "lt":
                return PathCondition(kernel_version_range=KernelVersionRange.less_than(kernel_version))
            case "-gt" | "gt":
                return PathCondition(kernel_version_range=KernelVersionRange.greater_than(kernel_version))
            case "-le" | "le":
                return PathCondition(kernel_version_range=KernelVersionRange.at_most(kernel_version))
            case "-ge" | "ge":
                return PathCondition(kernel_version_range=KernelVersionRange.at_least(kernel_version))
            case "-eq" | "eq":
                return PathCondition(kernel_version_range=KernelVersionRange.exactly(kernel_version))

        raise RuntimeError(f"Invalid operator in kernel_is command: {operator}")
