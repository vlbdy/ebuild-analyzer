from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.ast.enums.node_types import NodeType


class TestBashAST:
    def test_sanity(self, bash_parser: BashParser):
        bash = b"""
        command 1
        command 2 || command 3 && command 4
        if command 5; then
            command 6
        fi
    
        test_func() {
            command 7
        }
        """

        ast = bash_parser.parse(bash)
        assert len(ast.get_all_nodes_of_type(NodeType.COMMAND)) == 7
