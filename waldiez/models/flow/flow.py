# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.
"""Waldiez flow model."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from pydantic import Field, model_validator
from typing_extensions import Annotated, Literal, Self

from ..agents import WaldiezAgent
from ..chat import WaldiezChat
from ..common import WaldiezBase, now
from .flow_data import WaldiezFlowData


def id_factory() -> str:
    """Generate a unique ID.

    Returns
    -------
    str
        The unique ID.
    """
    now_td = datetime.now(timezone.utc)
    now_str = now_td.strftime("%Y%m%d%H%M%S%f")
    return f"{now_str}-{uuid.uuid4().hex}"


class WaldiezFlow(WaldiezBase):
    """Flow data class.

    Attributes
    ----------
    id : str
        The ID of the flow.
    type : Literal["flow"], optional
        The type of the "node" in a graph: "flow".
    name : str
        The name of the flow.
    description : str
        The description of the flow.
    tags : List[str]
        The tags of the flow.
    requirements : List[str]
        The requirements of the flow.
    storage_id : str
        The storage ID of the flow (ignored, UI related).
    created_at : str
        The date and time when the flow was created.
    updated_at : str
        The date and time when the flow was last updated.
    data : WaldiezFlowData
        The data of the flow. See `WaldiezFlowData`.
    """

    id: Annotated[
        str,
        Field(
            description="The ID of the flow",
            title="ID",
            default_factory=id_factory,
        ),
    ]
    type: Annotated[
        Literal["flow"],
        Field(
            "flow",
            description="The type of the 'node' in a graph",
            title="Type",
        ),
    ]
    name: Annotated[
        str,
        Field(
            ...,
            description="The name of the flow",
            title="Name",
        ),
    ]
    description: Annotated[
        str,
        Field(
            ...,
            description="The description of the flow",
            title="Description",
        ),
    ]
    tags: Annotated[
        List[str],
        Field(
            description="The tags of the flow",
            title="Tags",
            default_factory=list,
        ),
    ]
    requirements: Annotated[
        List[str],
        Field(
            description="The requirements of the flow",
            title="Requirements",
            default_factory=list,
        ),
    ]
    data: Annotated[
        WaldiezFlowData,
        Field(
            ...,
            description="The data of the flow",
            title="Data",
        ),
    ]
    storage_id: Annotated[
        str,
        Field(
            uuid.uuid4(),
            description="The storage ID of the flow (ignored, UI related)",
            title="Storage ID",
            alias="storageId",
        ),
    ]
    created_at: Annotated[
        str,
        Field(
            default_factory=now,
            title="Created At",
            description="The date and time when the flow was created.",
        ),
    ]
    updated_at: Annotated[
        str,
        Field(
            default_factory=now,
            title="Updated At",
            description="The date and time when the flow was last updated.",
        ),
    ]
    _ordered_flow: Optional[
        List[Tuple[WaldiezChat, WaldiezAgent, WaldiezAgent]]
    ] = None

    @property
    def is_async(self) -> bool:
        """Check if the flow is asynchronous.

        Returns
        -------
        bool
            True if the flow is asynchronous, False otherwise.
        """
        return self.data.is_async

    @property
    def is_swarm_flow(self) -> bool:
        """Check if the flow is a swarm flow.

        Returns
        -------
        bool
            True if the flow is a swarm flow, False otherwise.
        """
        return any(
            agent.agent_type == "swarm" for agent in self.data.agents.members
        )

    @property
    def ordered_flow(
        self,
    ) -> List[Tuple[WaldiezChat, WaldiezAgent, WaldiezAgent]]:
        """Get the ordered flow."""
        if not self._ordered_flow:
            self._ordered_flow = self._get_flow_order()
        return self._ordered_flow

    def get_agent_by_id(self, agent_id: str) -> WaldiezAgent:
        """Get the agent by ID.

        Parameters
        ----------
        agent_id : str
            The ID of the agent.

        Returns
        -------
        WaldiezAgent
            The agent.

        Raises
        ------
        ValueError
            If the agent with the given ID is not found.
        """
        for agent in self.data.agents.members:
            if agent.id == agent_id:
                return agent
        raise ValueError(f"Agent with ID {agent_id} not found.")

    def _get_flow_order(
        self,
    ) -> List[Tuple[WaldiezChat, WaldiezAgent, WaldiezAgent]]:
        """Get the ordered flow."""
        # in the chats, there is the 'order' field, we use this,
        # we only keep the ones with order >=0
        # and sort them by this property
        ordered_flow: List[Tuple[WaldiezChat, WaldiezAgent, WaldiezAgent]] = []
        # if swarm, we only keep the first chat
        if self.is_swarm_flow:
            ordered_flow = self._get_swarm_flow()
        if ordered_flow:
            return ordered_flow
        for chat in self.data.chats:
            if chat.data.order < 0:
                continue
            source = self.get_agent_by_id(chat.source)
            target = self.get_agent_by_id(chat.target)
            ordered_flow.append((chat, source, target))
        if not ordered_flow:
            if len(self.data.chats) == 1:
                chat = self.data.chats[0]
                source = self.get_agent_by_id(chat.source)
                target = self.get_agent_by_id(chat.target)
                ordered_flow.append((chat, source, target))
        return ordered_flow

    def _get_swarm_flow(
        self,
    ) -> List[Tuple[WaldiezChat, WaldiezAgent, WaldiezAgent]]:
        # valid "first" chat:
        # - source is a user|rag_user and target is a swarm
        # - source is a swarm and target is a swarm
        valid_chats = []
        for _chat in self.data.chats:
            target = self.get_agent_by_id(_chat.target)
            source = self.get_agent_by_id(_chat.source)
            if (
                source.agent_type in ["user", "rag_user"]
                and target.agent_type == "swarm"
            ):
                valid_chats.append(_chat)
            if source.agent_type == "swarm" and target.agent_type == "swarm":
                valid_chats.append(_chat)
        if not valid_chats:
            return []
        chat: Optional[WaldiezChat] = None
        # first check the order
        by_order = sorted(
            filter(lambda chat: chat.data.order >= 0, valid_chats),
            key=lambda chat: chat.data.order,
        )
        if not by_order:
            # let's order by position
            by_position = sorted(
                valid_chats,
                key=lambda chat: chat.data.position,
            )
            if by_position:
                chat = by_position[0]
            else:
                chat = valid_chats[0]
        else:
            chat = by_order[0]
        if chat:
            source = self.get_agent_by_id(chat.source)
            target = self.get_agent_by_id(chat.target)
            return [(chat, source, target)]
        return []

    def get_agent_connections(
        self, agent_id: str, all_chats: bool = True
    ) -> List[str]:
        """Get the agent connections.

        Parameters
        ----------
        agent_id : str
            The ID of the agent.
        all_chats : bool, optional
            If True, get the connections from all the chats, otherwise
            get the connections from the ordered flow (main chat flow).

        Returns
        -------
        List[str]
            The list of agent ids that the agent with the given ID connects to.
        """
        connections = []
        if all_chats:
            for chat in self.data.chats:
                if chat.source == agent_id:
                    connections.append(chat.target)
                if chat.target == agent_id:
                    connections.append(chat.source)
        else:
            for _, source, target in self.ordered_flow:
                if source.id == agent_id:
                    connections.append(target.id)
                if target.id == agent_id:
                    connections.append(source.id)
        return connections

    def get_group_chat_members(
        self, group_manager_id: str
    ) -> List[WaldiezAgent]:
        """Get the group chat members.

        Parameters
        ----------
        group_manager_id : str
            The ID of the group manager.

        Returns
        -------
        List[WaldiezAgent]
            The list of group chat
        """
        agent = self.get_agent_by_id(group_manager_id)
        if agent.agent_type != "manager":
            return []
        connections = self.get_agent_connections(
            group_manager_id,
            all_chats=True,
        )
        return [self.get_agent_by_id(member_id) for member_id in connections]

    def get_initial_swarm_agent(self) -> Optional[WaldiezAgent]:
        """Get the initial swarm agent.

        Returns
        -------
        Optional[WaldiezAgent]
            The initial swarm agent if found, None otherwise.
        """
        first_chat = self.ordered_flow[0]
        if (
            first_chat[1].agent_type == "swarm"
            or first_chat[2].agent_type == "swarm"
        ):
            return first_chat[1]
        for chat in self.data.chats:
            source_agent = self.get_agent_by_id(chat.source)
            if source_agent.agent_type == "swarm":
                return source_agent
            target_agent = self.get_agent_by_id(chat.target)
            if target_agent.agent_type == "swarm":
                return target_agent
        return None

    def get_swarm_chat_members(
        self,
        initial_agent: WaldiezAgent,
    ) -> Tuple[List[WaldiezAgent], Optional[WaldiezAgent]]:
        """Get the swarm chat members.

        Parameters
        ----------
        initial_agent : WaldiezAgent
            The initial agent.

        Returns
        -------
        Tuple[List[WaldiezAgent], Optional[WaldiezAgent]]
            The list of swarm chat members and the user agent if any.
        """
        members: List[WaldiezAgent] = []
        user_agent: Optional[WaldiezAgent] = None
        if initial_agent.agent_type != "swarm":
            return members, user_agent
        members.append(initial_agent)
        connections = self.get_agent_connections(
            initial_agent.id,
            all_chats=True,
        )
        for member_id in connections:
            member = self.get_agent_by_id(member_id)
            is_user = member.agent_type in ("user", "rag_user")
            if is_user and not user_agent:
                user_agent = member
        for agent in self.data.agents.members:
            if agent.agent_type == "swarm" and agent.id != initial_agent.id:
                members.append(agent)
        return members, user_agent

    def _validate_agent_connections(self) -> None:
        for agent in self.data.agents.members:
            if not any(
                agent.id in (chat.source, chat.target)
                for chat in self.data.chats
            ):
                raise ValueError(
                    f"Agent {agent.id} ({agent.name}) "
                    "does not connect to any other node."
                )
            # already covered above
            # if agent.agent_type == "manager":
            #     chat_member_ids = self.get_agent_connections(agent.id)
            #     if not chat_member_ids:
            #         raise ValueError(
            #             f"Manager's {agent.id} group chat has no members."
            #         )

    @model_validator(mode="after")
    def validate_flow(self) -> Self:
        """Flow validation.

        - unique node ids
        - there are at least two agents
        - all the agents connect to at least one other agent
        - all the linked agent skills are found in the flow
        - all the linked agent models are found in the flow
        - all the managers have at least one member in the chat group
        - the ordered flow (chats with position >=0) is not empty
        - all agents' code execution config functions exist in the flow skills
        - if swarm flow, there is at least one swarm agent

        Returns
        -------
        WaldiezFlow
            The validated flow.

        Raises
        ------
        ValueError
            If the ordered flow is empty.
            If the model IDs are not unique.
            If the skill IDs are not unique.
            If the agents do not connect to any other node.
            If the manager's group chat has no members.
        """
        if not self.ordered_flow:
            raise ValueError("The ordered flow is empty.")
        model_ids = [model.id for model in self.data.models]
        if len(model_ids) != len(set(model_ids)):
            raise ValueError("Model IDs must be unique.")
        skills_ids = [skill.id for skill in self.data.skills]
        if len(skills_ids) != len(set(skills_ids)):
            raise ValueError("Skill IDs must be unique.")
        self.data.agents.validate_flow(model_ids, skills_ids)
        self._validate_agent_connections()
        if self.is_swarm_flow and not self.get_initial_swarm_agent():
            raise ValueError("There is no initial swarm agent.")
        return self
