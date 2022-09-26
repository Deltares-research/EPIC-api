from pathlib import Path
from typing import Protocol

from epic_app.externals.external_script_arguments_protocol import (
    ExternalScriptArgumentsProtocol,
)


class ExternalRunnerProtocol(Protocol):
    output_dir: Path
    script_arguments: ExternalScriptArgumentsProtocol

    def run(self, *args, **kwargs) -> None:
        pass
