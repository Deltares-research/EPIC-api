import platform
import subprocess
from pathlib import Path
from typing import List, Optional, Type

from epic_app.externals.ERAMVisuals import eram_visuals_script
from epic_app.externals.external_wrapper_base import (
    ExternalRunner,
    ExternalRunnerOutput,
    ExternalWrapperBase,
    ExternalWrapperStatus,
)


class EramVisualsOutput:
    pdf_output: Optional[Path]
    png_output: Optional[Path]
    _base_output_name = "eram_visuals"

    def __init__(self, output_dir: Path) -> ExternalRunnerOutput:
        _base_name = output_dir / self._base_output_name
        self.pdf_output = _base_name.with_suffix(".pdf")
        self.png_output = _base_name.with_suffix(".png")


class EramVisualsRunner(ExternalRunner):
    def _get_windows_path(self) -> Path:
        # TODO: It should be retrieving it from the env / sys variable
        return Path("C:\\Program Files\\R\\R-4.2.1\\bin\\RScript.exe")

    def _get_platform_runner(self) -> Path:
        _system = platform.system()
        _bin_path = None
        if _system == "Windows":
            _bin_path = self._get_windows_path()
        elif _system == "Linux":
            _bin_path = Path("/usr/lib64/R/")
        else:
            raise NotImplementedError(
                f"ERAM Visuals not configured to run under {_system}"
            )

        if not _bin_path.exists():
            raise FileNotFoundError(f"No RScript.exe found at {_bin_path}")
        return _bin_path

    def run(self, *args, **kwargs) -> None:
        _command = [self._get_platform_runner()]
        assert eram_visuals_script.exists()
        _command.append(eram_visuals_script)
        _command.extend(kwargs.values())
        _return_call = subprocess.call(_command, shell=True)
        if _return_call != 0:
            raise ValueError("Execution failed.")


class EramVisualsWrapper(ExternalWrapperBase):

    _required_packages = ("scales", "ggplot2", "dplyr", "readr", "stringr")
    _status: ExternalWrapperStatus = None
    _output: EramVisualsOutput = None

    def __init__(self, input_file: Path, output_dir: Path) -> None:
        super().__init__()
        self._status = ExternalWrapperStatus()
        self._input_file = input_file
        self._output_dir = output_dir
        self._output = EramVisualsOutput(output_dir)

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
    def runner(self) -> ExternalRunner:
        return EramVisualsRunner()

    @property
    def output(self) -> ExternalRunnerOutput:
        return self._output

    def execute(self) -> None:
        try:
            self.initialize()
            self.runner.run(input_file=self._input_file, output_dir=self._output_dir)
            self.finalize()
        except Exception as e_info:
            self.finalize_with_error(str(e_info))
