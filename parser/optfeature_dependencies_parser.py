import shlex
from typing import List

from tree_sitter import Node

from parser.optfeature import OptFeatureDependencies


class OptFeatureDependenciesParser:
    def parse_optfeature_list_parent(self, list_parent: Node) -> OptFeatureDependencies:
        enabled_use_flag_dependencies: List[str] = []
        disabled_use_flag_dependencies: List[str] = []
        package_dependencies: List[str] = []

        for child in list_parent.children:
            text = child.text.decode()
            if text.startswith("use"):
                use_flag = shlex.split(text)[1]
                if use_flag.startswith('!'):
                    disabled_use_flag_dependencies.append(use_flag[1:])
                else:
                    enabled_use_flag_dependencies.append(use_flag)
            elif text.startswith("has_version"):
                package_dependencies.append(shlex.split(text)[1])

        return OptFeatureDependencies(enabled_use_flag_dependencies, disabled_use_flag_dependencies,
                                      package_dependencies)
