import pytest

from ebuild_analyzer.ast.bash_parser import BashParser


@pytest.fixture(scope='session')
def bash_parser() -> BashParser:
    return BashParser()
