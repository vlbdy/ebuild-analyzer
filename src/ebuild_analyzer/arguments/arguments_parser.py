from argparse import ArgumentParser

from ebuild_analyzer.arguments.config import Config


def parse() -> Config:
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
        "--run-unknown-commands", "--ruc",
        action="store_true",
        help="Run unknown commands to test whether they succeed or not. Some path conditions require commands to "
             "succeed or fail, enabling this option will let the analyzer try to execute the command to test whether "
             "the path condition is met. Use with caution!",
        default=False,
    )
    parser.set_defaults(show_ad_conditions=False)

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    optfeatures_parser = subparsers.add_parser(
        "optfeatures",
        help="Extract optfeatures",
    )
    optfeatures_parser.add_argument(
        "--no-ad-conditions", "--nac",
        dest="show_ad_conditions",
        action="store_false",
        help="Hide the conditions required for an optfeature to be advertised",
        default=True
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
    dump_ast_parser.add_argument("package", nargs="?")

    args = parser.parse_args()
    return Config(
        command=args.command,
        package=args.package,
        all=args.all,
        verbose=args.verbose,
        show_ad_conditions=args.show_ad_conditions,
        run_unknown_commands=args.run_unknown_commands,
    )
