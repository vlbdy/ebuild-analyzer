from typing import List

from ebuild_analyzer.kernel_config.checked.checked_kernel_config_key import CheckedKernelConfigKey
from ebuild_analyzer.kernel_config.local.local_kernel_config import LocalKernelConfig
from ebuild_analyzer.output.ansi import Color, Format
from ebuild_analyzer.output.printers.base_printer import BasePrinter
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.utils.conditional_message import ConditionalMessage
from ebuild_analyzer.utils.portage_db import PortageDatabase

"""
[purple]Checked kernel configuration for package <package>:
    [blue]Required kernel config keys to enable:
        [green/red, visible only if the conditions are met]KERNEL_CONFIG_KEY [gray, only if required](hard requirement)
            [gray, configurable visibility(default visible)]Checked when:
                /// same as optfeatures ///
            [gray, configurable visibility(default visible)]Notes:
                [gray]- <message>
                    [gray, configurable visibility]Printed when:
                        /// same as optfeatures ///
                [gray]- <message>
                    ...
        [green/red]KERNEL_CONFIG_KEY ...
            ...

    [blue]Kernel config keys to disable:
        /// same as above ///
"""


class CheckedKernelConfigPrinter(BasePrinter):
    def __init__(self, portage_db: PortageDatabase, run_unknown_commands: bool, local_kernel_config: LocalKernelConfig):
        super().__init__(portage_db, run_unknown_commands)
        self.__local_kernel_config = local_kernel_config

    def print(self, package_cpv: PackageCPV, checked_kernel_config_keys: List[CheckedKernelConfigKey]) -> None:
        self._buffer.reset()
        self._buffer.push(
            Color.LIGHT_PURPLE(Format.BOLD(f"Checked kernel configuration for package {package_cpv.text}:\n")))
        self._buffer.push_indent()

        enabled_kernel_config_keys = [key for key in checked_kernel_config_keys if key.enabled]
        disabled_kernel_config_keys = [key for key in checked_kernel_config_keys if not key.enabled]

        if enabled_kernel_config_keys:
            self._buffer.indented_push(Color.BLUE("Kernel config keys to enable:\n"))
        with self._buffer.scoped_indent():
            for key in enabled_kernel_config_keys:
                self.__print_colored_kernel_config_key(key)
                self.__print_checking_conditions(package_cpv, key)
                self.__print_notes(package_cpv, key)

        if disabled_kernel_config_keys:
            self._buffer.indented_push(Color.BLUE("Kernel config keys to disable:\n"))
        with self._buffer.scoped_indent():
            for key in disabled_kernel_config_keys:
                self.__print_colored_kernel_config_key(key, enabled_color=Color.RED, disabled_color=Color.GREEN)
                self.__print_checking_conditions(package_cpv, key)
                self.__print_notes(package_cpv, key)

        self._buffer.print()

    def __print_colored_kernel_config_key(self, key: CheckedKernelConfigKey, enabled_color: Color = Color.GREEN,
                                          disabled_color: Color = Color.RED) -> None:
        if self.__local_kernel_config.is_set(key.name):
            self._buffer.indented_push(enabled_color(key.name))
        else:
            self._buffer.indented_push(disabled_color(key.name))

        if key.required:
            self._buffer.push(" (hard requirement)")
        self._buffer.push('\n')

    def __print_checking_conditions(self, package_cpv: PackageCPV, key: CheckedKernelConfigKey) -> None:
        if not key.conditional_requirements:
            return

        with self._buffer.scoped_indent():
            self._buffer.indented_push("Checked when:\n")
            with self._buffer.scoped_indent():
                self.print_colored_path_conditions(package_cpv, key.conditional_requirements)

    def __print_notes(self, package_cpv: PackageCPV, key: CheckedKernelConfigKey) -> None:
        if not key.unmet_messages:
            return

        with self._buffer.scoped_indent():
            self._buffer.indented_push("Notes when this configuration is ")
            if key.enabled:
                self._buffer.push("disabled:\n")
            else:
                self._buffer.push("enabled:\n")

            with self._buffer.scoped_indent():
                for message in key.unmet_messages:
                    self._buffer.indented_push(f"- {message.message}\n")
                    self.__print_note_conditions(package_cpv, message)

    def __print_note_conditions(self, package_cpv: PackageCPV, message: ConditionalMessage) -> None:
        if not message.conditions:
            return

        with self._buffer.scoped_indent():
            self._buffer.indented_push("Printed when:\n")
            with self._buffer.scoped_indent():
                self.print_colored_path_conditions(package_cpv, message.conditions)
