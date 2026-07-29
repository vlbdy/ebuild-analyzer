from typing import List

from tree_sitter import Node

from ebuild_analyzer.ast import ast_node_utils
from ebuild_analyzer.ast.bash_ast import BashAST
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.kernel_config.checked.checked_kernel_config_key import CheckedKernelConfigKey
from ebuild_analyzer.kernel_config.checked.config_check_value_normalizer import ConfigCheckValueNormalizer
from ebuild_analyzer.kernel_config.checked.config_check_value_parser import ConfigCheckValueParser
from ebuild_analyzer.path_conditions.path_condition import PathCondition
from ebuild_analyzer.path_conditions.path_conditions_analyzer import PathConditionsAnalyzer


class CheckedKernelConfigExtractor:
    def __init__(self) -> None:
        self.__path_conditions_analyzer = PathConditionsAnalyzer()
        self.__config_check_value_normalizer = ConfigCheckValueNormalizer()
        self.__config_check_value_parser = ConfigCheckValueParser()

    def extract(self, ebuild_ast: BashAST) -> List[CheckedKernelConfigKey]:
        # In Bash grammar, variable assignment nodes in the AST always start with the name of the variable
        # on the leftmost side. This means that I can reliably look for all variable assignment nodes that start
        # with the name of the variable I want.
        config_check_assignment_nodes = ebuild_ast.get_all_nodes_of_type(NodeType.VARIABLE_ASSIGNMENT, "CONFIG_CHECK")
        return self.__extract_from_config_check_variables(config_check_assignment_nodes)

    def __extract_from_config_check_variables(self, config_check_variable_nodes: List[Node]) -> List[CheckedKernelConfigKey]:
        kernel_config_keys: List[CheckedKernelConfigKey] = []

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

    def __extract_single_node(self, node: Node, path_conditions: List[PathCondition]) -> List[CheckedKernelConfigKey]:
        kernel_config_keys: List[CheckedKernelConfigKey] = []

        kernel_configs_string = ast_node_utils.get_value_of_variable_assignment_node(node)
        if not kernel_configs_string:
            return kernel_config_keys
        kernel_configs_string = self.__config_check_value_normalizer.normalize(kernel_configs_string)

        kernel_configs = [kernel_config for kernel_config in kernel_configs_string.strip().split(' ') if kernel_config]

        for kernel_config in kernel_configs:
            kernel_config_key = self.__config_check_value_parser.parse(kernel_config)
            kernel_config_key.conditional_requirements = path_conditions

            kernel_config_keys.append(kernel_config_key)

        return kernel_config_keys
