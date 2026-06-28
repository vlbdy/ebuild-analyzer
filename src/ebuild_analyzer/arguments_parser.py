from argparse import ArgumentParser


def create() -> ArgumentParser:
    parser = ArgumentParser(prog="ebuild-analyzer")

    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Query all installed packages",
        default=False,
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose messages",
        default=False,
    )
    parser.add_argument(
        "--no-visibility-conditions", "--nvc",
        dest="show_visibility_conditions",
        action="store_false",
        help="Hide the conditions required for an optfeature to be visible",
        default=True
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    optfeatures_parser = subparsers.add_parser(
        "optfeatures",
        help="Extract optfeatures",
    )
    optfeatures_parser.add_argument("package", nargs="?")

    kernel_parser = subparsers.add_parser(
        "kernel-config",
        help="Extract kernel config requirements",
    )
    kernel_parser.add_argument("package", nargs="?")

    dump_ast_parser = subparsers.add_parser(
        "dump-ast",
        help="Dump tree sitter AST for the ebuild (for debugging)"
    )
    dump_ast_parser.add_argument("package")

    return parser
