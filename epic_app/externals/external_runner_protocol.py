from pathlib import Path
from typing import Protocol


class ExternalRunnerProtocol(Protocol):
    output_dir: Path

    def run(self, *args, **kwargs) -> None:
        pass
