import logging
import platform
import subprocess
from abc import abstractmethod
from os import environ
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
    def _set_logger(self, output_dir: Path) -> None:
        _log_file = output_dir / "eram.log"
        _log_file.unlink(missing_ok=True)
        _log_file.touch()
        _logger = logging.getLogger("")
        _logger.setLevel(logging.INFO)
        self._file_handler = logging.FileHandler(filename=_log_file, mode="w")
        self._file_handler.setLevel(logging.INFO)
        _logger.addHandler(self._file_handler)
        logging.info("Initialized")

    def _get_platform_runner(self) -> Path:
        # NOTE: Requires installing R in your system and defining a system variable
        # for the 'Rscript' executable.
        _rscript_path = environ.get("RSCRIPT")
        if not _rscript_path:
            raise NotImplementedError(
                f"ERAM Visuals REQUIRES an environment variable pointing to the Rscript location"
            )
        _rscript_path = Path(_rscript_path)
        if not _rscript_path.exists():
            raise FileNotFoundError(f"No RScript executable found at {_rscript_path}")
        return _rscript_path

    def _get_command_values(self, dict_values: dict) -> List[Path]:
        _rcommand = [eram_visuals_script]
        _rcommand.extend(dict_values.values())
        return _rcommand

    def run(self, *args, **kwargs) -> None:
        previous_exception = None
        assert eram_visuals_script.exists()
        self._set_logger(kwargs.get("output_dir", eram_visuals_script.parent))
        _command = ""
        try:
            _command = self._get_command(kwargs)
        except Exception as previous_exception:
            logging.error(previous_exception)
            _command = self._get_fallback_command(kwargs)
        if "windows" not in platform.platform().lower():
            _command = " ".join(_command)
        logging.info(_command)
        _return_call = subprocess.call(_command, shell=True)
        if _return_call != 0:
            if previous_exception:
                raise previous_exception
            raise ValueError(f"Execution failed with code {_return_call}")

    def _get_command(self, command_kwargs: List[Path]) -> str:
        _command_args = list(
            map(lambda x: x.as_posix(), self._get_command_values(command_kwargs))
        )
        _command = [self._get_platform_runner().as_posix(), "--verbose"]
        _command.extend(_command_args)
        logging.info(f"Platform runner found, args: {_command}")
        return _command

    def _get_fallback_command(self, command_kwargs: List[Path]) -> str:
        # Just give it a try in case it was not found a sys environment variable.
        _command_args = list(
            map(lambda x: x.as_posix(), self._get_command_values(command_kwargs))
        )
        _command = ["Rscript", "--verbose"]
        _command.extend(_command_args)
        logging.info(f"Fallback run with {_command}")
        return _command


class EramVisualsWrapper(ExternalWrapperBase):

    _required_packages = ("scales", "ggplot2", "dplyr", "readr", "stringr")
    _status: ExternalWrapperStatus = None
    _output: EramVisualsOutput = None
    _runner: ExternalRunner = None

    def __init__(
        self,
        input_file: Path,
        output_dir: Path,
        runner: Type[ExternalRunner] = EramVisualsRunner,
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
    def output(self) -> ExternalRunnerOutput:
        return self._output

    def execute(self) -> None:
        try:
            self.initialize()
            self._runner.run(input_file=self._input_file, output_dir=self._output_dir)
            self.finalize()
        except Exception as e_info:
            self.finalize_with_error(str(e_info))
