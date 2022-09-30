from typing import Protocol

from epic_app.externals.external_runner_output_protocol import (
    ExternalRunnerOutputProtocol,
)
from epic_app.externals.external_wrapper_status import ExternalWrapperStatus


class ExternalWrapperProtocol(Protocol):
    def execute(self, configuration_attrs: dict) -> None:
        pass

    @property
    def output(self) -> ExternalRunnerOutputProtocol:
        pass

    @property
    def status(self) -> ExternalWrapperStatus:
        pass
