import re
from typing import List

from tree_sitter import Node

from ebuild_analyzer.ast import ast_node_utils
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.kernel_config.kernel_config_key import KernelConfigKey
from ebuild_analyzer.path_conditions.path_condition import PathCondition
from ebuild_analyzer.path_conditions.path_conditions_analyzer import PathConditionsAnalyzer


class KernelConfigKeysExtractor:
    def __init__(self) -> None:
        self.__path_conditions_analyzer = PathConditionsAnalyzer()

    def extract(self, config_check_variable_nodes: List[Node]) -> List[KernelConfigKey]:
        kernel_config_keys: List[KernelConfigKey] = []

        for node in config_check_variable_nodes:
            if node.parent.type == NodeType.COMMAND:
                # This can happen in cases like `CONFIG_CHECK="..." linux-info_pkg_setup`
                # In this case we want the path conditions to be of the command because in the AST, the command itself
                # is the parent node of the variable assignment node, which messes up the path condition analysis.
                path_conditions = self.__path_conditions_analyzer.analyze(node.parent)
            else:
                path_conditions = self.__path_conditions_analyzer.analyze(node)

            kernel_config_keys += self.__extract_single_node(node, path_conditions)

        return kernel_config_keys

    def __extract_single_node(self, node: Node, path_conditions: List[PathCondition]) -> List[KernelConfigKey]:
        kernel_config_keys: List[KernelConfigKey] = []

        kernel_configs_string = ast_node_utils.get_value_of_variable_assignment_node(node)
        if not kernel_configs_string:
            return kernel_config_keys
        kernel_configs_string = self.__normalize_kernel_configs_string(kernel_configs_string)

        kernel_configs = [kernel_config for kernel_config in kernel_configs_string.strip().split(' ') if kernel_config]

        for kernel_config in kernel_configs:
            kernel_config_keys.append(self.__parse_kernel_config(kernel_config, path_conditions))

        return kernel_config_keys

    def __normalize_kernel_configs_string(self, kernel_configs_string: str) -> str:
        # CONFIG_CHECK variables are irrelevant.
        kernel_configs_string = kernel_configs_string.replace("${CONFIG_CHECK}", '')
        # Other variables are removed to ensure that the code doesn't break, although these cases should be fixed.
        kernel_configs_string = re.sub(r"[!~]*\$\{[^}]*}", "", kernel_configs_string)
        # Remove all the extra spaces everywhere
        kernel_configs_string = ' '.join(kernel_configs_string.split())
        return kernel_configs_string

    def __parse_kernel_config(self, raw_kernel_config: str, path_conditions: List[PathCondition]) -> KernelConfigKey:
        required = True
        enabled = True

        while not raw_kernel_config[0].isalpha():
            if raw_kernel_config[0] == '~':
                required = False
            elif raw_kernel_config[0] == '!':
                enabled = False
            raw_kernel_config = raw_kernel_config[1:]

        return KernelConfigKey(raw_kernel_config, enabled, required, path_conditions)
