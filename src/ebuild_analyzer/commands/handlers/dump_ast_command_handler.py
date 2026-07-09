from ebuild_analyzer.ast.bash_parser import BashParser
from ebuild_analyzer.commands.handlers.command_handler import CommandHandler
from ebuild_analyzer.ebuild.ebuild import Ebuild
from ebuild_analyzer.package_atoms.package_cpv import PackageCPV


class DumpAstCommandHandler(CommandHandler):
    def __init__(self) -> None:
        self.__bash_parser = BashParser()

    def handle(self, package_cpv: PackageCPV, ebuild: Ebuild) -> None:
        ebuild_ast = BashParser().parse(ebuild.contents)
        self.__dump_ast(ebuild_ast.get_tree().root_node, ebuild.contents)

    def __dump_ast(self, node, source, indent=0):
        text = source[node.start_byte:node.end_byte].decode("utf-8")

        print(
            " " * indent +
            f"[{node.type}] "
            f"'{text[:40].replace(chr(10), ' ')}'"
        )

        for child in node.children:
            self.__dump_ast(child, source, indent + 4)
