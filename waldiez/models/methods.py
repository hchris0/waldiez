"""Waldiez method classes and constants."""

# pylint: disable=line-too-long

from enum import Enum
from typing import Dict, List

from .agents import (
    CUSTOM_EMBEDDING_FUNCTION,
    CUSTOM_EMBEDDING_FUNCTION_ARGS,
    CUSTOM_EMBEDDING_FUNCTION_HINTS,
    CUSTOM_SPEAKER_SELECTION,
    CUSTOM_SPEAKER_SELECTION_ARGS,
    CUSTOM_SPEAKER_SELECTION_HINTS,
    CUSTOM_TEXT_SPLIT_FUNCTION,
    CUSTOM_TEXT_SPLIT_FUNCTION_ARGS,
    CUSTOM_TEXT_SPLIT_FUNCTION_HINTS,
    CUSTOM_TOKEN_COUNT_FUNCTION,
    CUSTOM_TOKEN_COUNT_FUNCTION_ARGS,
    CUSTOM_TOKEN_COUNT_FUNCTION_HINTS,
    IS_TERMINATION_MESSAGE,
    IS_TERMINATION_MESSAGE_ARGS,
    IS_TERMINATION_MESSAGE_HINTS,
)
from .chat import (
    CALLABLE_MESSAGE,
    CALLABLE_MESSAGE_ARGS,
    CALLABLE_MESSAGE_HINTS,
    NESTED_CHAT_ARGS,
    NESTED_CHAT_HINTS,
    NESTED_CHAT_MESSAGE,
    NESTED_CHAT_REPLY,
)


class WaldiezMethodName(str, Enum):
    """Waldiez method names."""

    CUSTOM_SPEAKER_SELECTION = CUSTOM_SPEAKER_SELECTION
    IS_TERMINATION_MESSAGE = IS_TERMINATION_MESSAGE
    CALLABLE_MESSAGE = CALLABLE_MESSAGE
    NESTED_CHAT_MESSAGE = NESTED_CHAT_MESSAGE
    NESTED_CHAT_REPLY = NESTED_CHAT_REPLY
    CUSTOM_EMBEDDING_FUNCTION = CUSTOM_EMBEDDING_FUNCTION
    CUSTOM_TEXT_SPLIT_FUNCTION = CUSTOM_TEXT_SPLIT_FUNCTION
    CUSTOM_TOKEN_COUNT_FUNCTION = CUSTOM_TOKEN_COUNT_FUNCTION


WaldiezMethodArgs: Dict[WaldiezMethodName, List[str]] = {
    WaldiezMethodName.CUSTOM_SPEAKER_SELECTION: CUSTOM_SPEAKER_SELECTION_ARGS,
    WaldiezMethodName.IS_TERMINATION_MESSAGE: IS_TERMINATION_MESSAGE_ARGS,
    WaldiezMethodName.CALLABLE_MESSAGE: CALLABLE_MESSAGE_ARGS,
    WaldiezMethodName.NESTED_CHAT_MESSAGE: NESTED_CHAT_ARGS,
    WaldiezMethodName.NESTED_CHAT_REPLY: NESTED_CHAT_ARGS,
    WaldiezMethodName.CUSTOM_EMBEDDING_FUNCTION: CUSTOM_EMBEDDING_FUNCTION_ARGS,  # noqa: E501
    WaldiezMethodName.CUSTOM_TEXT_SPLIT_FUNCTION: CUSTOM_TEXT_SPLIT_FUNCTION_ARGS,  # noqa: E501
    WaldiezMethodName.CUSTOM_TOKEN_COUNT_FUNCTION: CUSTOM_TOKEN_COUNT_FUNCTION_ARGS,  # noqa: E501
}

WaldiezMethodHints: Dict[WaldiezMethodName, str] = {
    WaldiezMethodName.CUSTOM_SPEAKER_SELECTION: CUSTOM_SPEAKER_SELECTION_HINTS,
    WaldiezMethodName.IS_TERMINATION_MESSAGE: IS_TERMINATION_MESSAGE_HINTS,
    WaldiezMethodName.CALLABLE_MESSAGE: CALLABLE_MESSAGE_HINTS,
    WaldiezMethodName.NESTED_CHAT_MESSAGE: NESTED_CHAT_HINTS,
    WaldiezMethodName.NESTED_CHAT_REPLY: NESTED_CHAT_HINTS,
    WaldiezMethodName.CUSTOM_EMBEDDING_FUNCTION: CUSTOM_EMBEDDING_FUNCTION_HINTS,  # noqa: E501
    WaldiezMethodName.CUSTOM_TEXT_SPLIT_FUNCTION: CUSTOM_TEXT_SPLIT_FUNCTION_HINTS,  # noqa: E501
    WaldiezMethodName.CUSTOM_TOKEN_COUNT_FUNCTION: CUSTOM_TOKEN_COUNT_FUNCTION_HINTS,  # noqa: E501
}
