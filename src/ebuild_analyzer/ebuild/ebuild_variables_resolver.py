from typing import Dict

from ebuild_analyzer.ast import ast_node_utils
from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.ast.enums.node_types import NodeType
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV
from ebuild_analyzer.utils import variable_expander
from ebuild_analyzer.utils.portage_db import PortageDatabase


class EbuildVariablesResolver:
    def __init__(self, portage_db: PortageDatabase) -> None:
        self.__portage_db = portage_db

    def resolve_all(self, package_cpv: PackageCPV, ebuild_contents: bytes) -> Dict[str, str]:
        all_variables = self.resolve_default_variables(package_cpv)
        all_variables.update(self.resolve_metadata_variables(package_cpv))
        all_variables.update(self.resolve_bash_variables(ebuild_contents))
        return all_variables

    def resolve_metadata_variables(self, package_cpv: PackageCPV) -> Dict[str, str]:
        # These are metadata variables which were used somewhere in an optfeature
        metadata_keys = ("SLOT",)
        metadata_variables: Dict[str, str] = dict()

        for key in metadata_keys:
            metadata_variables[key] = self.__portage_db.get_metadata_key(package_cpv, key)
        return metadata_variables

    @staticmethod
    def resolve_default_variables(package_cpv: PackageCPV) -> Dict[str, str]:
        category = package_cpv.category
        package_name = package_cpv.package
        package_version = package_cpv.version
        package_revision = package_cpv.revision

        # r0 revisions are omitted in the PF variable
        if package_revision == "r0":
            full_package = f"{package_name}-{package_version}"
        else:
            full_package = f"{package_name}-{package_version}-{package_revision}"

        return {
            "P": f"{package_name}-{package_version}",
            "PN": package_name,
            "PV": package_version,
            "PR": package_revision,
            "PVR": f"{package_version}-{package_revision}",
            "PF": full_package,
            "CATEGORY": category,
        }

    @staticmethod
    def resolve_bash_variables(ebuild_contents: bytes) -> Dict[str, str]:
        bash_ast = BashParser().parse(ebuild_contents)
        variable_assignment_nodes = bash_ast.get_all_nodes_of_type(NodeType.VARIABLE_ASSIGNMENT)

        raw_variables: Dict[str, str] = dict()
        for variable_assignment in variable_assignment_nodes:
            variable_name = ast_node_utils.get_variable_name_from_variable_assignment_node(variable_assignment)
            value = ast_node_utils.get_value_of_variable_assignment_node(variable_assignment)

            # Handle self referencing variables
            if f"${variable_name}" in value or f"${{{variable_name}}}" in value:
                if variable_name in raw_variables:
                    value = variable_expander.expand_variable(value.encode(), variable_name, raw_variables[variable_name])
                    value = value.decode()
                else:
                    # Skip the variable if it self-references and we don't know any value for it
                    continue

            raw_variables[variable_name] = value

        return raw_variables
