from pathlib import Path
from typing import Optional

from epic_app.externals.external_runner_output_protocol import (
    ExternalRunnerOutputProtocol,
)


class EramVisualsOutput:
    pdf_output: Optional[Path]
    png_output: Optional[Path]
    _base_output_name = "eram_visuals"

    def __init__(self, output_dir: Path) -> ExternalRunnerOutputProtocol:
        _base_name = output_dir / self._base_output_name
        self.pdf_output = _base_name.with_suffix(".pdf")
        self.png_output = _base_name.with_suffix(".png")
