import sys

from ebuild_analyzer.arguments import arguments_parser, config_validator
from ebuild_analyzer.arguments.config_validator import InvalidConfigException
from ebuild_analyzer.commands.command_dispatcher import CommandDispatcher
from ebuild_analyzer.output.ansi import Color


def main():
    config = arguments_parser.parse()
    try:
        config_validator.validate(config)
    except InvalidConfigException as e:
        print(Color.RED("error: ") + str(e))
        sys.exit(1)

    CommandDispatcher(config).dispatch()


if __name__ == "__main__":
    main()
