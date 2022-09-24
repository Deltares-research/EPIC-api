from pathlib import Path
from typing import Type

from epic_app.externals.ERAMVisuals.eram_visuals_output import EramVisualsOutput
from epic_app.externals.ERAMVisuals.eram_visuals_runner import EramVisualsRunner
from epic_app.externals.external_runner_protocol import ExternalRunnerProtocol
from epic_app.externals.external_wrapper_protocol import ExternalWrapperProtocol
from epic_app.externals.external_wrapper_status import ExternalWrapperStatus


class EramVisualsWrapper(ExternalWrapperProtocol):

    _required_packages = ("scales", "ggplot2", "dplyr", "readr", "stringr")
    _status: ExternalWrapperStatus = None
    _output: EramVisualsOutput = None
    _runner: ExternalRunnerProtocol = None

    def __init__(
        self,
        input_file: Path,
        output_dir: Path,
        runner: Type = EramVisualsRunner,
    ) -> None:
        super().__init__()
        self._status = ExternalWrapperStatus()
        self._input_file = input_file
        self._output_dir = output_dir
        self._output = EramVisualsOutput(output_dir)
        self._runner = runner()

    @property
    def status(self) -> ExternalWrapperStatus:
        return self._status

    def _get_backup_output_file(self, output_file: Path) -> Path:
        return output_file.with_suffix(output_file.suffix + ".old")

    def initialize(self) -> None:
        self._status.to_initialized()
        if not self._output_dir.exists():
            self._output_dir.mkdir(parents=True)

        def initialize_backup(from_file: Path) -> None:
            _to_file = self._get_backup_output_file(from_file)
            _to_file.unlink(missing_ok=True)
            if from_file.is_file():
                from_file.rename(_to_file)

        initialize_backup(self._output.png_output)
        initialize_backup(self._output.pdf_output)

    def _finalize_backup_file(self, failed: bool) -> None:
        def apply_backup(to_file: Path) -> None:
            _from_file = self._get_backup_output_file(to_file)
            if failed:
                # Then we need to bring back the backup as a file.
                to_file.unlink(missing_ok=True)
                # Rename the backup to be the source file.
                if _from_file.exists():
                    _from_file.rename(to_file)
            # Remove the backup file and leave only the 'real one'.
            _from_file.unlink(missing_ok=True)

        apply_backup(self._output.png_output)
        apply_backup(self._output.pdf_output)

    def finalize(self) -> None:
        self._status.to_succeeded()
        self._finalize_backup_file(failed=False)

    def finalize_with_error(self, error_mssg: str) -> None:
        # Execution failed
        self._status.to_failed(error_mssg)
        self._finalize_backup_file(failed=True)

    @property
    def output(self) -> EramVisualsOutput:
        return self._output

    def execute(self) -> None:
        try:
            self.initialize()
            self._runner.run(input_file=self._input_file, output_dir=self._output_dir)
            self.finalize()
        except Exception as e_info:
            self.finalize_with_error(str(e_info))
