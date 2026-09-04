from typing import List

from ebuild_analyzer.utils.conditional_message import ConditionalMessage


def merge_conditional_messages_with_same_conditions(messages: List[ConditionalMessage]) -> List[ConditionalMessage]:
    merged_messages: List[ConditionalMessage] = []

    for current_message in messages:
        was_merged = False
        for merged_message in merged_messages:
            if (current_message.conditions == merged_message.conditions
                    and current_message.severity == merged_message.severity):
                merged_message.message += current_message.message
                was_merged = True
                break
        if not was_merged:
            merged_messages.append(current_message)

    return merged_messages
