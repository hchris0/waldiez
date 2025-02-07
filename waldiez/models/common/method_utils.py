# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.
"""Function related utilities."""

import ast
import importlib.util
import sys
import sysconfig
from typing import List, Optional, Tuple

import parso
import parso.python
import parso.tree

MAX_VAR_NAME_LENGTH = 64


def is_standard_library(module_name: str) -> bool:
    """Check if the module is part of the standard library.

    Parameters
    ----------
    module_name : str
        The module name.

    Returns
    -------
    bool
        True if the module is part of the standard library.
    """
    if module_name in sys.builtin_module_names:
        return True
    try:
        spec = importlib.util.find_spec(module_name)
    except BaseException:  # pylint: disable=broad-except
        return False
    if spec is None or not spec.origin:
        return False
    if "site-packages" in spec.origin:
        return False
    if spec.origin.startswith(sys.prefix) or spec.origin == "frozen":
        return True
    stdlib_path = sysconfig.get_path("stdlib")
    return spec.origin.startswith(stdlib_path)


def parse_code_string(
    code_string: str,
) -> Tuple[Optional[str], Optional[ast.Module]]:
    """Parse the code string.

    Parameters
    ----------
    code_string : str
        The code string.

    Returns
    -------
    Tuple[Optional[str], Optional[ast.Module]]
        If valid, None and the ast module.
        If invalid, the error message and None.
    """
    # pylint: disable=broad-except
    try:
        tree = ast.parse(code_string)
    except SyntaxError as e:
        return f"SyntaxError: {e}, in " + "\n" + f"{code_string}", None
    except BaseException as e:  # pragma: no cover
        return f"Invalid code: {e}, in " + "\n" + f"{code_string}", None
    return None, tree


def gather_code_imports(
    code_string: str,
    is_interop: bool,
) -> Tuple[List[str], List[str]]:
    """Gather the imports from the code string.

    Parameters
    ----------
    code_string : str
        The code string.
    is_interop : bool
        If True, make sure the interoperability import is present.

    Returns
    -------
    Tuple[List[str], List[str]]
        The standard library imports and the third party imports.
    """
    standard_lib_imports: List[str] = []
    third_party_imports: List[str] = []
    tree = parso.parse(code_string)  # type: ignore
    for node in tree.iter_imports():
        if node.type == "import_name":
            full_import_statement = node.get_code().strip()
            module_name = (
                node.get_code().replace("import", "").strip().split(" ")[0]
            )
            if not module_name:
                continue
            if is_standard_library(module_name):
                standard_lib_imports.append(full_import_statement)
            else:
                third_party_imports.append(full_import_statement)
        elif node.type == "import_from":
            full_import_statement = node.get_code().strip()
            module_name = (
                node.get_code().replace("from", "").strip().split(" ")[0]
            )
            if not module_name:
                continue
            if is_standard_library(module_name):
                standard_lib_imports.append(full_import_statement)
            else:
                third_party_imports.append(full_import_statement)
    if is_interop and (
        "from autogen.interop import Interoperability"
        not in third_party_imports
    ):
        third_party_imports.append(
            "from autogen.interop import Interoperability"
        )
    # sorted_standard_lib_imports =  # first import x, then from a import b
    sorted_standard_lib_imports = sorted(
        [stmt for stmt in standard_lib_imports if stmt.startswith("import ")]
    ) + sorted(
        [stmt for stmt in standard_lib_imports if stmt.startswith("from ")]
    )
    sorted_third_party_imports = sorted(
        [stmt for stmt in third_party_imports if stmt.startswith("import ")]
    ) + sorted(
        [stmt for stmt in third_party_imports if stmt.startswith("from ")]
    )
    return sorted_standard_lib_imports, sorted_third_party_imports


def check_function(
    code_string: str,
    function_name: str,
    function_args: List[str],
) -> Tuple[bool, str]:
    """Check the function.

    Parameters
    ----------
    code_string : str
        The code string to check.
    function_name : str
        The expected method name.
    function_args : List[str]
        The expected method arguments.
    Returns
    -------
    Tuple[bool, str]
        If valid, True and the function body (only), no extra lines.
        If invalid, False and the error message.
    """
    error, tree = parse_code_string(code_string)
    if error is not None or tree is None:
        return False, error or "Invalid code"
    return _validate_function_body(
        tree,
        code_string,
        function_name,
        function_args,
    )


def _validate_function_body(
    tree: ast.Module,
    code_string: str,
    function_name: str,
    function_args: List[str],
) -> Tuple[bool, str]:
    """Get the function body.

    Parameters
    ----------
    tree : ast.Module
        The ast module.
    function_body : str
        The function body.
    function_name : str
        The expected method name.
    function_args : List[str]
        The expected method arguments.
    Returns
    -------
    Tuple[bool, str]
        If valid, True and the function body (only), no extra lines.
        If invalid, False and the error message.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name != function_name:
                continue
            if len(node.args.args) != len(function_args):
                return (
                    False,
                    (
                        f"Invalid number of arguments, in function {node.name},"
                        f" expected: {len(function_args)},"
                        f" got: {len(node.args.args)} :("
                    ),
                )
            for arg, expected_arg in zip(node.args.args, function_args):
                if arg.arg != expected_arg:
                    return (
                        False,
                        (
                            f"Invalid argument name: {arg.arg}"
                            f" in function {node.name}"
                        ),
                    )
            if not node.body:  # pragma: no cover
                return False, "No body found in the function"
            function_body = _get_function_body(code_string, node)
            return True, function_body
    error_msg = (
        f"No method with name `{function_name}`"
        f" and arguments `{function_args}` found"
    )
    return False, error_msg


def get_function(
    code_string: str,
    function_name: str,
) -> str:
    """Get the function signature and body.

    Parameters
    ----------
    code_string : str
        The code string.
    function_name : str
        The function name.

    Returns
    -------
    str
        The function signature and body.
    """
    tree = parso.parse(code_string)  # type: ignore
    for node in tree.iter_funcdefs():
        if node.name.value == function_name:
            return node.get_code()
    return ""


def _get_function_body(
    code_string: str,
    node: ast.FunctionDef,
) -> str:
    """Get the function body, including docstring and comments inside.

    Parameters
    ----------
    code_string : str
        The code string.
    node : ast.FunctionDef
        The function node.

    Returns
    -------
    str
        The function body.

    Raises
    ------
    ValueError
        If no body found in the function.
    """
    lines = code_string.splitlines()
    signature_start_line = node.lineno - 1
    body_start_line = node.body[0].lineno - 1
    signature_end_line = signature_start_line
    for i in range(signature_start_line, body_start_line):
        if ")" in lines[i]:
            signature_end_line = i
            break
    function_body_lines = lines[signature_end_line + 1 :]
    last_line = function_body_lines[-1]
    if not last_line.strip() and len(function_body_lines) > 1:
        function_body_lines = function_body_lines[:-1]
    function_body = "\n".join(function_body_lines)
    while function_body.startswith("\n"):
        function_body = function_body[1:]
    while function_body.endswith("\n"):
        function_body = function_body[:-1]
    return function_body


def generate_function(
    function_name: str,
    function_args: List[str],
    function_types: Tuple[List[str], str],
    function_body: str,
    types_as_comments: bool = False,
) -> str:
    """Generate a function.

    Parameters
    ----------
    function_name : str
        The function name.
    function_args : List[str]
        The function arguments.
    function_types : Tuple[List[str], str]
        The function types.
    function_body : str
        The function body.
    types_as_comments : bool, optional
        Include the type hints as comments (or in the function signature)
        (default is False).
    Returns
    -------
    str
        The generated function.
    """
    if len(function_name) > MAX_VAR_NAME_LENGTH:
        function_name = function_name[:MAX_VAR_NAME_LENGTH]
    function_string = f"def {function_name}("
    if not function_args:
        function_string += ")"
    else:
        function_string += "\n"
        for arg, arg_type in zip(function_args, function_types[0]):
            if types_as_comments:
                function_string += f"    {arg},  # type: {arg_type}" + "\n"
            else:
                function_string += f"    {arg}: {arg_type}," + "\n"
        function_string += ")"
    if types_as_comments:
        function_string += ":\n"
        function_string += "    # type: (...) -> " + function_types[1]
    else:
        function_string += " -> " + function_types[1] + ":"
    function_string += "\n" if not function_body.startswith("\n") else ""
    function_string += f"{function_body}"
    if not function_string.endswith("\n"):
        function_string += "\n"
    return function_string
