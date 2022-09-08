import enum
import typing


class ExternalWrapperStatusType(enum):
    READY = 0
    INITIALIZED = 1
    SUCCEEDED = 2
    FAILED = 3


class ExternalWrapperStatus:
    status_type: ExternalWrapperStatusType = ExternalWrapperStatusType.READY
    status_info: str = ""

    def __str__(self) -> str:
        return self.status_info


class ExternalWrapperBase(typing.Protocol):
    def execute(self, configuration_attrs: dict) -> None:
        pass

    @property
    def status(self) -> ExternalWrapperStatus:
        pass
