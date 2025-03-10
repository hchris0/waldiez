# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.
# flake8: noqa: E501
# pylint: disable=too-many-locals,too-many-statements,line-too-long
"""Common functions for testing waldiez.exporting.agent.AgentExporter."""

from typing import List, Tuple, Type

from waldiez.models import (
    WaldiezAgent,
    WaldiezAgentType,
    WaldiezAssistant,
    WaldiezGroupManager,
    WaldiezModel,
    WaldiezRagUser,
    WaldiezReasoningAgent,
    WaldiezSkill,
    WaldiezSwarmAgent,
    WaldiezUserProxy,
)


def create_agent(
    counter: int,
    agent_type: WaldiezAgentType,
) -> Tuple[WaldiezAgent, List[WaldiezSkill], List[WaldiezModel]]:
    """Create an agent.

    Parameters
    ----------
    agent_type : WaldiezAgentType
        The agent type.
    counter : int
        The counter to use for the id and name.

    Returns
    -------
    WaldiezAgent
        The agent.
    """
    # fmt: off
    skill1 = WaldiezSkill(  # type: ignore
        id=f"ws-{counter}_1",
        name=f"skill{counter}_1",
        description=f"skill{counter}_1 description",
        data={  # type: ignore
            "content": f"def skill{counter}_1():" + "\n" + f'    return "skill body of skill{counter}_1"',
            "secrets": {
                "SECRET_KEY_1": "SECRET_VALUE_1",
                "SECRET_KEY_2": "SECRET_VALUE_2",
            },
        },
    )
    skill2 = WaldiezSkill(  # type: ignore
        id=f"ws-{counter}_2",
        name=f"skill{counter}_2",
        description=f"skill{counter}_2 description",
        data={  # type: ignore
            "content": f"def skill{counter}_2():" + "\n" + f'    return "skill body of skill{counter}_2"',
            "secrets": {},
        },
    )
    # fmt: on
    model1 = WaldiezModel(  # type: ignore
        id=f"wm-{counter}_1",
        name=f"model{counter}_1",
        description=f"model{counter}_1 description",
        data={"apiType": "anthropic"},  # type: ignore
    )
    model2 = WaldiezModel(  # type: ignore
        id=f"wm-{counter}_2",
        name=f"model{counter}_2",
        description=f"model{counter}_2 description",
        data={"apiType": "nim"},  # type: ignore
    )
    agent_cls: Type[WaldiezAgent] = WaldiezAgent
    if agent_type == "user":
        agent_cls = WaldiezUserProxy
    if agent_type == "assistant":
        agent_cls = WaldiezAssistant
    if agent_type == "rag_user":
        agent_cls = WaldiezRagUser
    if agent_type == "manager":
        agent_cls = WaldiezGroupManager
    if agent_type == "swarm":
        agent_cls = WaldiezSwarmAgent
    if agent_type == "reasoning":
        agent_cls = WaldiezReasoningAgent
    agent = agent_cls(  # type: ignore
        id=f"wa-{counter}",
        name=f"agent{counter}",
        description=f"agent{counter} description",
        data={  # type: ignore
            "system_message": f"system message of agent {counter}",
            "skills": [
                {
                    "id": f"ws-{counter}_1",
                    "executor_id": f"wa-{counter}",
                },
                {
                    "id": f"ws-{counter}_2",
                    "executor_id": f"wa-{counter}",
                },
            ],
            "model_ids": [f"wm-{counter}_1", f"wm-{counter}_2"],
        },
    )
    return agent, [skill1, skill2], [model1, model2]
