"""Waldiez Message Model."""

from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import Field
from typing_extensions import Annotated, Literal

from ..common import WaldiezBase, check_function

WaldiezChatMessageType = Literal[
    "string", "method", "rag_message_generator", "none"
]


class WaldiezChatMessage(WaldiezBase):
    """
    Waldiez Message.

    A generic message with a type and content.

    If the type is not `none`, the content is a string.
    If the type is 'method', the content is the source code of a method.
    If the type is 'last_carryover', the content is a method to return
        the last carryover from the context.
    If the type is 'rag_message_generator', and the sender is a RAG user agent,
        the content will be generated by the `sender.message_generator` method.

    Attributes
    ----------
    type : WaldiezChatMessageType
        The type of the message:
        - string
        - method
        - rag_message_generator
        - none
        If the sender is a RAG user agent,
        and the type is `rag_message_generator`,
        the `{sender}.message_generator` method will be used.
    content : Optional[str]
        The content of the message (string or method).
    context : Dict[str, Any]
        Extra context of the message.
    """

    type: Annotated[
        WaldiezChatMessageType,
        Field(
            "none",
            title="Type",
            description=(
                "The type of the message: "
                "`string`, `method`, "
                "`rag_message_generator` or `none`."
                "If last_carryover, a method to return the context's"
                "last carryover will be used."
                "If the sender is a RAG user agent, "
                "and the type is `message_generator`,"
                "the `sender.message_generator` method will be used."
            ),
        ),
    ]
    use_carryover: Annotated[
        bool,
        Field(
            False,
            title="Use Carryover",
            description="Use the carryover from the context.",
        ),
    ]
    content: Annotated[
        Optional[str],
        Field(
            None,
            title="Content",
            description="The content of the message (string or method).",
        ),
    ]
    context: Annotated[
        Dict[str, Any],
        Field(
            default_factory=dict,
            title="Context",
            description="Extra context of the message.",
        ),
    ]


def validate_message_dict(
    value: Dict[
        Literal["type", "use_carryover", "content", "context"],
        Union[Optional[str], Optional[bool], Optional[Dict[str, Any]]],
    ],
    function_name: str,
    function_args: List[str],
    type_hints: str,
    skip_definition: bool = False,
) -> WaldiezChatMessage:
    """Validate a message dict.

    Check the provided message dict.
    Depending on the type, the content is validated.
    If the type is "method", the content is checked against the function name.

    Parameters
    ----------
    value : dict
        The message dict.
    function_name : str
        The method name.
    function_args : List[str]
        The expected method arguments.
    type_hints : str
        The type hints to include.
    skip_definition : bool, optional
        Skip the function definition in the content, by default False

    Returns
    -------
    WaldiezChatMessage
        The validated message.

    Raises
    ------
    ValueError
        If the validation fails.
    """
    message_type, use_carryover, content, context = _get_message_args_from_dict(
        value
    )
    if message_type == "string":
        if not content or not isinstance(content, str):
            content = ""
        if use_carryover:
            method_content = _get_last_carryover_method_content(content)
            return WaldiezChatMessage(
                type="method",
                use_carryover=True,
                content=method_content,
                context=context,
            )
        return WaldiezChatMessage(
            type="string",
            use_carryover=False,
            content=content,
            context=context,
        )
    if message_type == "none":
        return WaldiezChatMessage(
            type="none",
            use_carryover=False,
            content=None,
            context=context,
        )
    if message_type == "method":
        if not content:
            raise ValueError(
                "The message content is required for the method type"
            )
        valid, error_or_content = check_function(
            code_string=content,
            function_name=function_name,
            function_args=function_args,
            type_hints=type_hints,
        )
        if not valid:
            raise ValueError(error_or_content)
        message_content = error_or_content if skip_definition else content
        return WaldiezChatMessage(
            type="method",
            use_carryover=use_carryover,
            content=message_content,
            context=context,
        )
    if message_type == "rag_message_generator":
        if use_carryover:
            return WaldiezChatMessage(
                type="method",
                use_carryover=True,
                content=RAG_METHOD_WITH_CARRYOVER,
                context=context,
            )
        return WaldiezChatMessage(
            type="rag_message_generator",
            use_carryover=use_carryover,
            content=None,
            context=context,
        )
    raise ValueError("Invalid message type")  # pragma: no cover


def _get_message_args_from_dict(
    value: Dict[
        Literal["type", "use_carryover", "content", "context"],
        Union[Optional[str], Optional[bool], Optional[Dict[str, Any]]],
    ],
) -> Tuple[str, bool, Optional[str], Dict[str, Any]]:
    """Get the message args from a dict.

    Parameters
    ----------
    value : dict
        The message dict.

    Returns
    -------
    tuple
        The message type, content, and context.

    Raises
    ------
    ValueError
        If the message type is invalid.
    """
    message_type = value.get("type")
    if not isinstance(message_type, str) or message_type not in (
        "string",
        "method",
        "rag_message_generator",
        "none",
    ):
        raise ValueError("Invalid message type")
    use_carryover = value.get("use_carryover", False)
    if not isinstance(use_carryover, bool):
        use_carryover = False
    content = value.get("content", "")
    if not isinstance(content, str):
        content = ""
    context: Dict[str, Any] = {}
    context_value = value.get("context")
    if isinstance(context_value, dict):
        context = context_value
    if not isinstance(context, dict):  # pragma: no cover
        context = {}
    return message_type, use_carryover, content, context


def _get_last_carryover_method_content(text_content: str) -> str:
    """Get the last carryover method content.

    Parameters
    ----------
    text_content : str
        Text content before the carryover.
    Returns
    -------
    str
        The last carryover method content.
    """
    method_content = '''
def callable_message(sender, recipient, context):
    # type: (ConversableAgent, ConversableAgent, dict) -> Union[dict, str]
    """Get the message to send using the last carryover.

    Parameters
    ----------
    sender : ConversableAgent
        The source agent.
    recipient : ConversableAgent
        The target agent.
    context : dict
        The context.

    Returns
    -------
    Union[dict, str]
        The message to send using the last carryover.
    """
    carryover = context.get("carryover", "")
    if isinstance(carryover, list):
        carryover = carryover[-1]
    if not isinstance(carryover, str):
        carryover = ""'''
    if text_content:
        method_content += f"""
    final_message = "{text_content}" + carryover
    return final_message
"""
    else:
        method_content += """
    return carryover
"""
    return method_content


RAG_METHOD_WITH_CARRYOVER = '''
def callable_message(sender, recipient, context):
    # type: (RetrieveUserProxyAgent, ConversableAgent, dict) -> Union[dict, str]
    """Get the message using the RAG message generator method.

    Parameters
    ----------
    sender : RetrieveUserProxyAgent
        The source agent.
    recipient : ConversableAgent
        The target agent.
    context : dict
        The context.

    Returns
    -------
    Union[dict, str]
        The message to send using the last carryover.
    """
    carryover = context.get("carryover", "")
    if isinstance(carryover, list):
        carryover = carryover[-1]
    if not isinstance(carryover, str):
        carryover = ""
    message = sender.message_generator(sender, recipient, context)
    if carryover:
        message += carryover
    return message
'''
