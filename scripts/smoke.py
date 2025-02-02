# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.
"""Check if we can load and convert the examples in the git repo.

No model api keys or skill secrets files are checked.
If conversion fails or if the outputs in
../.local/examples/[x]/[y].py are not as expected,
something is wrong with latest changes in the codebase.
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import urllib3
from urllib3 import Timeout

try:
    from waldiez.exporter import WaldiezExporter
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from waldiez.exporter import WaldiezExporter

ROOT_DIR = Path(__file__).resolve().parents[1]
DOT_LOCAL = ROOT_DIR / ".local"
DOT_LOCAL.mkdir(exist_ok=True, parents=True)

REPO_URL = "https://raw.githubusercontent.com/waldiez/examples/refs/heads/main"
EXAMPLES = [
    "01 - Standup Comedians/Standup Comedians 1.waldiez",
    "01 - Standup Comedians/Standup Comedians 2.waldiez",
    "01 - Standup Comedians/Standup Comedians 3.waldiez",
    "02 - On-boarding/On-boarding.waldiez",
    "03 - Reflection/Reflection.waldiez",
    "04 - Tools/Tool Use.waldiez",
    "05 - Coding/Coding.waldiez",
    "06 - Planning/Planning 1.waldiez",
    "06 - Planning/Planning 2.waldiez",
    "07 - Group chat with RAG/RAG.waldiez",
    "08 - ReAct using Tavily/ReAct.waldiez",
    "09 - AutoDefence/AutoDefense Flow.waldiez",
    "10 - Travel Planning/Travel Planning.waldiez",
    "11 - Swarm/Swarm.waldiez",
    "12 - Reasoning/Chain-of-Thought Reasoning with DFS.waldiez",
]


def download_example(example_url: str, example_path: str) -> None:
    """Download an example from the git repo.

    Parameters
    ----------
    example_url : str
        The URL of the example.
    example_path : str
        The path to save the example.

    Raises
    ------
    Exception
        If the download fails.

    """
    timeout = Timeout(connect=10.0, read=30.0)
    pool = urllib3.PoolManager(timeout=timeout)
    response = pool.request("GET", example_url)
    if response.status != 200:
        # pylint: disable=broad-exception-raised
        raise Exception(f"Failed to download {example_url}")
    flow_data = json.loads(response.data.decode("utf-8"))
    with open(example_path, "w", encoding="utf-8") as file:
        json.dump(flow_data, file)


def move_to_dot_local(example_dir: str, example_path: str) -> None:
    """Move the converted example to the .local directory.

    Parameters
    ----------
    example_dir : str
        The directory of the example.
    example_path : str
        The path to the example.
    """
    example_name = os.path.basename(example_path)
    dot_local_dir = os.path.join(DOT_LOCAL, "examples", example_dir)
    os.makedirs(dot_local_dir, exist_ok=True)
    dot_local_path = os.path.join(dot_local_dir, example_name)
    shutil.move(example_path, dot_local_path)
    dot_local_py_path = dot_local_path.replace(".waldiez", ".py")
    shutil.move(example_path.replace(".waldiez", ".py"), dot_local_py_path)


def convert_examples() -> None:
    """Check if we can load and convert the examples in the git repo.

    Raises
    ------
    Exception
        If the conversion fails.
    """
    temp_dir = tempfile.mkdtemp()
    for example in EXAMPLES:
        print(f"Converting {example}")
        example_dir = os.path.dirname(example)
        example_url = f"{REPO_URL}/{example}"
        example_path = os.path.join(temp_dir, example)
        os.makedirs(os.path.dirname(example_path), exist_ok=True)
        download_example(example_url, example_path)
        flow = WaldiezExporter.load(Path(example_path))
        output_path = example_path.replace(".waldiez", ".py")
        WaldiezExporter.export(flow, output_path)
        if not os.path.exists(output_path):
            # pylint: disable=broad-exception-raised
            raise Exception(f"Failed to convert {example}")
        move_to_dot_local(example_dir, example_path)
    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    convert_examples()
