# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.
"""Test waldiez.exporting.models.ModelsExporter."""

import shutil
from pathlib import Path

from waldiez.exporting.models import ModelsExporter
from waldiez.models.agents import WaldiezAgent
from waldiez.models.model import DEFAULT_BASE_URLS, WaldiezModel


# pylint: disable=too-many-locals,too-many-statements
def test_models_exporter(tmp_path: Path) -> None:
    """Test ModelsExporter.

    Parameters
    ----------
    tmp_path : Path
        The temporary path.
    """

    flow_name = "flow1"
    model1_name = "model1"
    model2_name = "model2"
    model3_name = "model3"
    agent = WaldiezAgent(
        id="wa-1",
        name="agent1",
        agent_type="assistant",
        description="agent description",
        data={  # type: ignore
            "model_ids": ["wm-1", "wm-2"],
        },
    )
    agent_names = {"wa-1": "agent1"}
    model1 = WaldiezModel(
        id="wm-1",
        name=model1_name,
        description="model description",
        data={"apiType": "anthropic"},  # type: ignore
    )
    model2 = WaldiezModel(
        id="wm-2",
        name=model2_name,
        description="model description",
        data={"apiType": "nim"},  # type: ignore
    )
    model3 = WaldiezModel(
        id="wm-3",
        name=model3_name,
        description="model description",
        data={"apiType": "google"},  # type: ignore
    )
    model_names = {
        "wm-1": model1_name,
        "wm-2": model2_name,
        "wm-3": model3_name,
    }
    models_exporter = ModelsExporter(
        flow_name=flow_name,
        agents=[agent],
        agent_names=agent_names,
        models=[model1, model2, model3],
        model_names=model_names,
        for_notebook=False,
        output_dir=None,
        cache_seed=42,
    )
    imports = models_exporter.get_imports()
    assert imports is None
    generated_string = models_exporter.generate()
    expected = f"""
{model1_name}_llm_config = {{
    "model": "{model1_name}",
    "api_type": "anthropic",
    "api_key": get_{flow_name}_model_api_key("{model1_name}")
}}

{model2_name}_llm_config = {{
    "model": "{model2_name}",
    "api_key": get_{flow_name}_model_api_key("{model2_name}"),
    "base_url": "{DEFAULT_BASE_URLS["nim"]}"
}}

{model3_name}_llm_config = {{
    "model": "{model3_name}",
    "api_type": "google",
    "api_key": get_{flow_name}_model_api_key("{model3_name}")
}}
"""
    assert generated_string == expected
    output_dir = tmp_path / "test_models_exporter"
    output_dir.mkdir(exist_ok=True)
    models_exporter = ModelsExporter(
        flow_name=flow_name,
        agents=[agent],
        agent_names=agent_names,
        models=[model1, model2],
        model_names=model_names,
        for_notebook=True,
        output_dir=str(tmp_path),
        cache_seed=42,
    )
    imports = models_exporter.get_imports()
    assert imports is not None
    expected_import_string = (
        f"from {flow_name}_api_keys import ("
        "\n"
        f"    get_{flow_name}_model_api_key,"
        "\n"
        ")\n"
    )
    assert imports[0][0] == expected_import_string
    assert imports[0][1].name == "LOCAL"
    after_export = models_exporter.get_after_export()
    assert after_export is not None
    assert after_export[0][0] == (
        "    llm_config={\n"
        '        "config_list": [\n'
        f"            {model1_name}_llm_config," + "\n"
        f"            {model2_name}_llm_config," + "\n"
        "        ],\n"
        '        "cache_seed": 42,\n'
        "    },\n"
    )
    assert (tmp_path / f"{flow_name}_api_keys.py").exists()
    shutil.rmtree(output_dir)

    agent = WaldiezAgent(
        id="wa-1",
        name="agent1",
        agent_type="assistant",
        description="agent description",
        data={  # type: ignore
            "model_ids": [],
        },
    )
    models_exporter = ModelsExporter(
        flow_name=flow_name,
        agents=[agent],
        agent_names=agent_names,
        models=[model1, model2, model3],
        model_names=model_names,
        for_notebook=False,
        output_dir=str(tmp_path),
        cache_seed=43,
    )
    assert models_exporter.get_imports() is not None
    generated_string = models_exporter.generate()
    assert generated_string == expected
    output_dir = tmp_path / "test_models_exporter"
    output_dir.mkdir(exist_ok=True)
    models_exporter = ModelsExporter(
        flow_name=flow_name,
        agents=[agent],
        agent_names=agent_names,
        models=[model1, model2],
        model_names=model_names,
        for_notebook=True,
        output_dir=str(tmp_path),
        cache_seed=None,
    )
    imports = models_exporter.get_imports()
    assert imports is not None
    expected_import_string = (
        f"from {flow_name}_api_keys import (" + "\n"
        f"    get_{flow_name}_model_api_key," + "\n"
        ")\n"
    )
    assert imports[0][0] == expected_import_string
    assert imports[0][1].name == "LOCAL"
    assert (tmp_path / f"{flow_name}_api_keys.py").exists()
    shutil.rmtree(output_dir)

    agent = WaldiezAgent(
        id="wa-1",
        name="agent1",
        agent_type="assistant",
        description="agent description",
        data={  # type: ignore
            "model_ids": [],
        },
    )
    models_exporter = ModelsExporter(
        flow_name=flow_name,
        agents=[agent],
        agent_names=agent_names,
        models=[model1, model2],
        model_names=model_names,
        for_notebook=False,
        output_dir=str(tmp_path),
        cache_seed=None,
    )
    assert models_exporter.get_imports() is not None
    after_export = models_exporter.get_after_export()
    assert after_export is not None
    assert after_export[0][0] == "    llm_config=False,\n"
