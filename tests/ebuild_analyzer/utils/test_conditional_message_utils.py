from typing import List

import pytest

from ebuild_analyzer.path_conditions.path_condition import PathCondition
from ebuild_analyzer.utils import conditional_message_utils
from ebuild_analyzer.utils.conditional_message import ConditionalMessage, MessageSeverity


@pytest.mark.parametrize("messages, expected", [
    (
            [ConditionalMessage("a", MessageSeverity.ERROR, []), ConditionalMessage("b", MessageSeverity.ERROR, [])],
            [ConditionalMessage("ab", MessageSeverity.ERROR, [])]
    ),
    (
            [ConditionalMessage("a", MessageSeverity.WARNING, []), ConditionalMessage("b", MessageSeverity.ERROR, [])],
            [ConditionalMessage("a", MessageSeverity.WARNING, []), ConditionalMessage("b", MessageSeverity.ERROR, [])]
    ),
    (
            [ConditionalMessage("a", MessageSeverity.ERROR, [PathCondition()]),
             ConditionalMessage("b", MessageSeverity.ERROR, [])],
            [ConditionalMessage("a", MessageSeverity.ERROR, [PathCondition()]),
             ConditionalMessage("b", MessageSeverity.ERROR, [])]
    ),
    ([], []),
])
def test_merge_conditional_messages_with_same_conditions(messages: List[ConditionalMessage],
                                                         expected: List[ConditionalMessage]):
    assert conditional_message_utils.merge_conditional_messages_with_same_conditions(messages) == expected
