import subprocess
from typing import Collection, Iterable, List

from ebuild_analyzer.kernel_version.kernel_version_range import KernelVersionRange
from ebuild_analyzer.kernel_version.local_kernel_version import get_local_kernel_version
from ebuild_analyzer.output.ansi import Color, Format
from ebuild_analyzer.output.output_buffer import OutputBuffer
from ebuild_analyzer.package_atoms.package_atom import PackageAtom
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.path_conditions.path_condition import PathCondition
from ebuild_analyzer.utils.portage_db import PortageDatabase


class BasePrinter:
    def __init__(self, portage_db: PortageDatabase, run_unknown_commands: bool) -> None:
        self._portage_db = portage_db
        self._run_unknown_commands = run_unknown_commands
        self._buffer = OutputBuffer()

    def print_package_atoms(self, package_atoms: Collection[PackageAtom], installed_color: Color = Color.GREEN,
                            uninstalled_color: Color = Color.RED) -> None:
        for i, package_atom in enumerate(package_atoms):
            self.print_package_atom(package_atom, installed_color, uninstalled_color)

            if i != len(package_atoms) - 1:
                self._buffer.push(', ')

    def print_package_atom(self, package_atom: PackageAtom, installed_color: Color = Color.GREEN,
                           uninstalled_color: Color = Color.RED):
        if not self._portage_db.does_package_exist(package_atom) or self._portage_db.is_package_masked(
                package_atom):
            self.print_non_installable_package(package_atom)
            return

        self.print_colored_package_atom(package_atom, installed_color, uninstalled_color)

        package_cpv = self.get_most_relevant_cpv(package_atom)
        if package_atom.required_enabled_use_flags or package_atom.required_disabled_use_flags:
            self._buffer.push('[')
        if package_atom.required_enabled_use_flags:
            self.print_use_flags_to_enable_list(package_cpv, package_atom.required_enabled_use_flags)
            if package_atom.required_disabled_use_flags:
                self._buffer.push(', ')
        if package_atom.required_disabled_use_flags:
            self.print_use_flags_to_disable_list(package_cpv, package_atom.required_disabled_use_flags)
        if package_atom.required_enabled_use_flags or package_atom.required_disabled_use_flags:
            self._buffer.push(']')

    def print_use_flags_to_disable_list(self, package_cpv: PackageCPV, use_flags: Collection[str]) -> None:
        for i, use_flag in enumerate(use_flags):
            self.print_colored_use_flag_to_disable(package_cpv, use_flag)

            if i != len(use_flags) - 1:
                self._buffer.push(', ')

    def print_use_flags_to_enable_list(self, package_cpv: PackageCPV, use_flags: Collection[str]) -> None:
        for i, use_flag in enumerate(use_flags):
            self.print_colored_use_flag_to_enable(package_cpv, use_flag)

            if i != len(use_flags) - 1:
                self._buffer.push(', ')

    def print_package_combination(self, package_combo: List[PackageAtom]) -> None:
        with self._buffer.scoped_indent():
            for i, package_atom in enumerate(package_combo):
                self._buffer.indented_push("")
                self.print_package_atom(package_atom)

                if i != len(package_combo) - 1:
                    self._buffer.push(Format.BOLD(" and "))
                    self._buffer.disable_indentation()
        self._buffer.enable_indentation()

    def print_colored_use_flag_to_disable(self, package_cpv: PackageCPV, use_flag: str) -> None:
        if not self._portage_db.is_use_flag_enabled(package_cpv, use_flag):
            self._buffer.push(Color.GREEN(f"-{use_flag}"))
        else:
            self._buffer.push(Color.RED(f"-{use_flag}"))

    def print_colored_use_flag_to_enable(self, package_cpv: PackageCPV, use_flag: str) -> None:
        if self._portage_db.is_use_flag_enabled(package_cpv, use_flag):
            self._buffer.push(Color.GREEN(use_flag))
        else:
            self._buffer.push(Color.RED(use_flag))

    def print_colored_package_atom(self, package_atom: PackageAtom, installed_color: Color = Color.GREEN,
                                   uninstalled_color: Color = Color.RED) -> None:
        if self._portage_db.is_package_installed(package_atom):
            self._buffer.push(installed_color(package_atom.text))
        else:
            self._buffer.push(uninstalled_color(package_atom.text))

    def print_non_installable_package(self, package_atom: PackageAtom) -> None:
        use_flags = ','.join(package_atom.required_enabled_use_flags)
        use_flags += ','.join(package_atom.required_disabled_use_flags)
        self._buffer.push(f"{package_atom.text}")
        if use_flags:
            self._buffer.push(f"[{use_flags}]")

    def print_commands(self, commands: Iterable[str]) -> None:
        for command in commands:
            if self._run_unknown_commands:
                self.print_colored_command(command)
            else:
                self._buffer.indented_push(command)
            self._buffer.push('\n')

    def print_colored_command(self, command: str) -> None:
        result = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            self._buffer.indented_push(Color.GREEN(command))
        else:
            self._buffer.indented_push(Color.RED(command))

    def print_colored_kernel_version_range(self, kernel_version_range: KernelVersionRange) -> None:
        if kernel_version_range.contains(get_local_kernel_version()):
            self._buffer.push(Color.GREEN(str(kernel_version_range)))
        else:
            self._buffer.push(Color.RED(str(kernel_version_range)))

    def get_most_relevant_cpv(self, package_atom: PackageAtom) -> PackageCPV:
        if self._portage_db.is_package_installed(package_atom):
            return self._portage_db.get_best_installed_cpv(package_atom)
        else:
            return self._portage_db.get_best_visible_cpv(package_atom)

    def print_colored_path_conditions(self, package_cpv: PackageCPV, conditions: List[PathCondition]) -> None:
        for i, condition in enumerate(conditions):
            self.print_colored_path_condition(package_cpv, condition)
            if i != len(conditions) - 1:
                self._buffer.push_indent()
                self._buffer.indented_push(Format.BOLD(" or\n"))
                self._buffer.pop_indent()

    def print_colored_path_condition(self, package_cpv: PackageCPV, condition: PathCondition) -> None:
        if condition.installed_packages:
            self._buffer.indented_push("The following packages are installed: [")
            self.print_package_atoms(condition.installed_packages)
            self._buffer.push("]\n")

        if condition.uninstalled_packages:
            self._buffer.indented_push("The following packages are not installed: [")
            self.print_package_atoms(condition.uninstalled_packages,
                                     installed_color=Color.RED, uninstalled_color=Color.GREEN)
            self._buffer.push("]\n")

        if condition.enabled_use_flags:
            self._buffer.indented_push("The following USE flags are enabled: [")
            self.print_use_flags_to_enable_list(package_cpv, condition.enabled_use_flags)
            self._buffer.push("]\n")

        if condition.disabled_use_flags:
            self._buffer.indented_push("The following USE flags are disabled: [")
            self.print_use_flags_to_disable_list(package_cpv, condition.disabled_use_flags)
            self._buffer.push("]\n")

        if condition.successful_commands:
            self._buffer.indented_push("The following commands succeed:\n")
            with self._buffer.scoped_indent():
                self.print_commands(condition.successful_commands)

        if condition.failed_commands:
            self._buffer.indented_push("The following commands fail:\n")
            with self._buffer.scoped_indent():
                self.print_commands(condition.failed_commands)

        if condition.kernel_version_range is not None:
            self._buffer.indented_push("Kernel version in range: ")
            self.print_colored_kernel_version_range(condition.kernel_version_range)
            self._buffer.push('\n')
