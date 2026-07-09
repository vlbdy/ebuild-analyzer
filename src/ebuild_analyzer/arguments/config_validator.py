from ebuild_analyzer.arguments.config import Config


class InvalidConfigException(Exception):
    pass


def validate(config: Config) -> None:
    if not config.package and not config.all:
        raise InvalidConfigException("PACKAGE is required unless --all is specified")
