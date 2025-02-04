# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.
# pylint: disable=protected-access
"""Test WaldiezRunner."""

import shutil
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from autogen.io import IOStream  # type: ignore

from waldiez.models import Waldiez, WaldiezFlow
from waldiez.runner import WaldiezRunner
from waldiez.running.running import get_printer


class CustomIOStream(IOStream):
    """Custom IOStream class."""

    def print(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Print objects.

        Parameters
        ----------
        objects : Any
            Objects to print.
        sep : str, optional
            Separator, by default " ".
        end : str, optional
            End, by default 'eol'.
        flush : bool, optional
            Whether to flush, by default False.
        """
        print(*objects, sep=sep, end=end, flush=flush)

    def input(self, prompt: str = "", *, password: bool = False) -> str:
        """Get user input.

        Parameters
        ----------
        prompt : str, optional
            Prompt, by default "".
        password : bool, optional
            Whether to read a password, by default False.

        Returns
        -------
        str
            User input.
        """
        with patch("builtins.input", return_value="User Input\n"):
            return input(prompt)


IOStream.set_global_default(CustomIOStream())


def test_waldiez_runner(
    waldiez_flow: WaldiezFlow,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test WaldiezRunner.

    Parameters
    ----------
    waldiez_flow : WaldiezFlow
        A WaldiezFlow instance.
    tmp_path : Path
        Pytest fixture to create temporary directory.
    capsys : pytest.CaptureFixture[Optional[str]]
        Pytest fixture to capture stdout and stderr.
    """
    waldiez = Waldiez.from_dict(data=waldiez_flow.model_dump(by_alias=True))
    output_path = tmp_path / "output.py"
    runner = WaldiezRunner(waldiez)
    with IOStream.set_default(CustomIOStream()):
        runner.run(output_path=output_path, skip_mmd=True)
    std_out = capsys.readouterr().out
    assert "Starting workflow" in std_out
    assert (tmp_path / "waldiez_out").exists()
    shutil.rmtree(tmp_path / "waldiez_out")


@pytest.mark.timeout(600)
def test_waldiez_runner_requirements_with_captain_agent(
    waldiez_flow_with_captain_agent: WaldiezFlow,
) -> None:
    """Test WaldiezRunner with requirements when captain agent is present.

    Parameters
    ----------
    waldiez_flow_with_captain_agent : WaldiezFlow
    """
    waldiez = Waldiez.from_dict(
        data=waldiez_flow_with_captain_agent.model_dump(by_alias=True)
    )
    runner = WaldiezRunner(waldiez)
    with IOStream.set_default(CustomIOStream()):
        runner.install_requirements()


def test_waldiez_with_invalid_requirement(
    capsys: pytest.CaptureFixture[str],
    waldiez_flow: WaldiezFlow,
) -> None:
    """Test Waldiez with invalid requirement.

    Parameters
    ----------
    capsys : pytest.CaptureFixture[str]
        Pytest fixture to capture stdout and stderr.
    waldiez_flow : WaldiezFlow
        A WaldiezFlow instance.
    """
    flow_dict = waldiez_flow.model_dump(by_alias=True)
    # add an invalid requirement
    flow_dict["requirements"] = ["invalid_requirement"]
    waldiez = Waldiez.from_dict(data=flow_dict)
    runner = WaldiezRunner(waldiez)
    runner.install_requirements()
    std_err = capsys.readouterr().out
    assert (
        "ERROR: No matching distribution found for invalid_requirement"
        in std_err
    )


class BadIOStream(IOStream):
    """Bad IOStream class."""

    def print(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        flush: bool = False,
    ) -> None:
        """Print objects.

        Parameters
        ----------
        objects : Any
            Objects to print.
        sep : str, optional
            Separator, by default " ".
        end : str, optional
            End, by default 'eol'.
        flush : bool, optional
            Whether to flush, by default False.

        Raises
        ------
        UnicodeEncodeError
            If the string is invalid
        """
        raise UnicodeEncodeError("utf-8", "", 0, 1, "invalid string")


def test_get_printer(capsys: pytest.CaptureFixture[str]) -> None:
    """Test get_printer.

    Parameters
    ----------
    capsys : pytest.CaptureFixture[str]
        Pytest fixture to capture stdout and stderr.
    """
    printer = get_printer()
    invalid_str = "This is an invalid string: 🤯"
    printer(invalid_str)
    assert "This is an invalid string: " in capsys.readouterr().out
    invalid_encoded = "This is an invalid encoded string".encode("cp1252")
    printer(invalid_encoded)
    assert "This is an invalid encoded string" in capsys.readouterr().out
    with IOStream.set_default(BadIOStream()):
        printer1 = get_printer()
        printer1(invalid_str)
    IOStream.set_global_default(CustomIOStream())
