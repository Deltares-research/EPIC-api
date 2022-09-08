import typing
from enum import Enum


class ExternalWrapperStatusType(Enum):
    READY = 0
    INITIALIZED = 1
    SUCCEEDED = 2
    FAILED = 3


class ExternalWrapperStatus:
    status_type: ExternalWrapperStatusType = ExternalWrapperStatusType.READY
    status_info: str = ""

    def __init__(self) -> None:
        self.status_info = ""
        self.status_type = ExternalWrapperStatusType.READY

    def __str__(self) -> str:
        _info = {
            ExternalWrapperStatusType.READY: "Ready",
            ExternalWrapperStatusType.INITIALIZED: "Initialized",
            ExternalWrapperStatusType.SUCCEEDED: "Succeeded",
            ExternalWrapperStatusType.FAILED: f"Failed: {self.status_info}",
        }
        return _info[self.status_type]

    def _change_status(
        self, new_status: ExternalWrapperStatusType, message: str
    ) -> None:
        self.status_type = new_status
        self.status_info = message

    def to_ready(self, message: str = "") -> None:
        self._change_status(ExternalWrapperStatusType.READY, message)

    def to_initialized(self, message: str = "") -> None:
        self._change_status(ExternalWrapperStatusType.INITIALIZED, message)

    def to_succeeded(self, message: str = "") -> None:
        self._change_status(ExternalWrapperStatusType.SUCCEEDED, message)

    def to_failed(self, message: str) -> None:
        self._change_status(ExternalWrapperStatusType.FAILED, message)


class ExternalWrapperBase(typing.Protocol):
    def execute(self, configuration_attrs: dict) -> None:
        pass

    @property
    def status(self) -> ExternalWrapperStatus:
        pass
