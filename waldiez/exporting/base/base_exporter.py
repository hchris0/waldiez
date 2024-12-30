"""Base exporter class to be inherited by all exporters."""

import abc
from typing import Any, List, Optional, Tuple, TypedDict, Union

from .agent_position import AgentPosition
from .export_position import ExportPosition
from .import_position import ImportPosition


class ExporterReturnType(TypedDict):
    """Exporter Return Type."""

    content: Optional[str]
    imports: Optional[List[Tuple[str, ImportPosition]]]
    environment_variables: Optional[List[Tuple[str, str]]]
    before_export: Optional[
        List[Tuple[str, Union[ExportPosition, AgentPosition]]]
    ]
    after_export: Optional[
        List[Tuple[str, Union[ExportPosition, AgentPosition]]]
    ]


class BaseExporter(abc.ABC):
    """Base exporter."""

    @abc.abstractmethod
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the exporter.

        Parameters
        ----------
        *args
            The positional arguments.
        **kwargs
            The keyword arguments.
        """
        raise NotImplementedError("Method not implemented.")

    def get_environment_variables(self) -> Optional[List[Tuple[str, str]]]:
        """Get the environment variables to set.

        Returns
        -------
        Optional[Set[Tuple[str, str]]]
            The environment variables to set if any.
        """

    def get_imports(self) -> Optional[List[Tuple[str, ImportPosition]]]:
        """ "Generate the imports string for the exporter.

        Returns
        -------
        Optional[Tuple[str, ImportPosition]]
            The exported imports and the position of the imports.
        """

    def get_before_export(
        self,
    ) -> Optional[List[Tuple[str, Union[ExportPosition, AgentPosition]]]]:
        """Generate the content before the main export.

        Returns
        -------
        Optional[List[Tuple[str, Union[ExportPosition, AgentPosition]]]]
            The exported content before the main export and its position.
        """

    def generate(
        self,
    ) -> Optional[str]:
        """Generate the main export.

        Returns
        -------
        str
            The exported content.
        """

    def get_after_export(
        self,
    ) -> Optional[List[Tuple[str, Union[ExportPosition, AgentPosition]]]]:
        """Generate the content after the main export.

        Returns
        -------
        Optional[List[Tuple[str, Union[ExportPosition, AgentPosition]]]]
            The exported content after the main export and its position.
        """

    @abc.abstractmethod
    def export(self) -> ExporterReturnType:
        """Export the content.

        Returns
        -------
        ExporterReturnType
            The exported content.
        """
