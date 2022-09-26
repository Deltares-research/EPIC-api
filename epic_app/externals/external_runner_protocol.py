from pathlib import Path
from typing import Protocol

from epic_app.externals.try_hard_script_arguments_protocol import (
    TryHardScriptArgumentsProtocol,
)


class ExternalRunnerProtocol(Protocol):
    output_dir: Path
    script_arguments: TryHardScriptArgumentsProtocol

    def run(self, *args, **kwargs) -> None:
        pass
