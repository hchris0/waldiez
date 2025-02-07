# SPDX-License-Identifier: Apache-2.0.
# Copyright (c) 2024 - 2025 Waldiez and contributors.
"""Waldiez Skill model."""

from typing import Dict, List, Tuple

from pydantic import Field, model_validator
from typing_extensions import Annotated, Literal, Self

from ..common import (
    WaldiezBase,
    gather_code_imports,
    get_function,
    now,
    parse_code_string,
)
from .skill_data import WaldiezSkillData, WaldiezSkillType

SHARED_SKILL_NAME = "waldiez_shared"


class WaldiezSkill(WaldiezBase):
    """Waldiez Skill.

    Attributes
    ----------
    id : str
        The ID of the skill.
    type : Literal["skill"]
        The type of the "node" in a graph: "skill".
    name : str
        The name of the skill.
    description : str
        The description of the skill.
    tags : List[str]
        The tags of the skill.
    requirements : List[str]
        The requirements of the skill.
    created_at : str
        The date and time when the skill was created.
    updated_at : str
        The date and time when the skill was last updated.
    data : WaldiezSkillData
        The data of the skill. See `WaldiezSkillData`.
    """

    id: Annotated[
        str, Field(..., title="ID", description="The ID of the skill.")
    ]
    type: Annotated[
        Literal["skill"],
        Field(
            default="skill",
            title="Type",
            description="The type of the 'node' in a graph.",
        ),
    ]
    name: Annotated[
        str, Field(..., title="Name", description="The name of the skill.")
    ]
    description: Annotated[
        str,
        Field(
            ...,
            title="Description",
            description="The description of the skill.",
        ),
    ]
    tags: Annotated[
        List[str],
        Field(
            title="Tags",
            description="The tags of the skill.",
            default_factory=list,
        ),
    ]
    requirements: Annotated[
        List[str],
        Field(
            title="Requirements",
            description="The requirements of the skill.",
            default_factory=list,
        ),
    ]
    data: Annotated[
        WaldiezSkillData,
        Field(..., title="Data", description="The data of the skill."),
    ]
    created_at: Annotated[
        str,
        Field(
            default_factory=now,
            title="Created At",
            description="The date and time when the skill was created.",
        ),
    ]
    updated_at: Annotated[
        str,
        Field(
            default_factory=now,
            title="Updated At",
            description="The date and time when the skill was last updated.",
        ),
    ]

    @property
    def skill_type(self) -> WaldiezSkillType:
        """Get the skill type.

        Returns
        -------
        WaldiezSkillType
            The type of the skill [shared, custom, langchain, crewai, pydantic].
        """
        return self.data.skill_type

    _skill_imports: Tuple[List[str], List[str]] = ([], [])

    def get_imports(self) -> Tuple[List[str], List[str]]:
        """Get the skill imports.

        Returns
        -------
        Tuple[List[str], List[str]]
            The builtin and external imports.
        """
        return self._skill_imports

    @property
    def is_shared(self) -> bool:
        """Check if the skill is shared.

        Returns
        -------
        bool
            True if the skill is shared, False otherwise.
        """
        return self.skill_type == "shared" or self.name == SHARED_SKILL_NAME

    def get_content(self) -> str:
        """Get the content of the skill.

        Returns
        -------
        str
            The content of the skill.
        """
        if self.is_shared or self.skill_type in (
            "langchain",
            "crewai",
            "pydantic",
        ):
            return self.data.content
        # if custom, only the function content
        return get_function(self.data.content, self.name)

    @model_validator(mode="after")
    def validate_data(self) -> Self:
        """Validate the data.

        Returns
        -------
        WaldiezSkill
            The skill.

        Raises
        ------
        ValueError
            If the skill name is not in the content.
            If the skill content is invalid.
        """
        search = f"def {self.name}("
        if self.skill_type == "custom" and not self.is_shared:
            if search not in self.data.content:
                raise ValueError(
                    f"The skill name '{self.name}' is not in the content."
                )
            error, tree = parse_code_string(self.data.content)
            if error is not None or tree is None:
                raise ValueError(f"Invalid skill content: {error}")
        if self.skill_type in ("langchain", "crewai", "pydantic"):
            # we expect a var with that name
            # and should exclude any {skill.name}.register_* calls
            expected = f"{self.name} = "
            if expected not in self.data.content:
                raise ValueError(
                    f"The skill name '{self.name}' is not in the content."
                )
        # we can't use here
        # "agent.register_for_llm(...)" or"
        # "agent.register_for_execution(...)" or
        # "skill_name.register_..." calls
        # since we need the agent's name in these calls
        to_exclude = [
            f"{self.name}.register_for",
            ".register_for_llm(",
            ".register_for_execution(",
        ]
        if any(exclude in self.data.content for exclude in to_exclude):
            content_without_it = "\n".join(
                line
                for line in self.data.content.splitlines()
                if all(exclude not in line for exclude in to_exclude)
            )
            error, tree = parse_code_string(content_without_it)
            if error is not None or tree is None:
                raise ValueError(f"Invalid skill content: {error}")
            self.data.content = content_without_it
        self._skill_imports = gather_code_imports(self.data.content)
        # remove the imports from the content
        # we 'll place them at the top of the file
        all_imports = self._skill_imports[0] + self._skill_imports[1]
        code_lines = self.data.content.splitlines()
        valid_lines = [
            line
            for line in code_lines
            if not any(line.startswith(imp) for imp in all_imports)
        ]
        # remove empty lines at the beginning and end
        # of the content
        while valid_lines and not valid_lines[0].strip():
            valid_lines.pop(0)
        while valid_lines and not valid_lines[-1].strip():
            valid_lines.pop()
        self.data.content = "\n".join(valid_lines)
        return self

    @property
    def content(self) -> str:
        """Get the content (source) of the skill."""
        return self.data.content

    @property
    def secrets(self) -> Dict[str, str]:
        """Get the secrets (environment variables) of the skill."""
        return self.data.secrets or {}
