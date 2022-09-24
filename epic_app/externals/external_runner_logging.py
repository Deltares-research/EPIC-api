from __future__ import annotations

import logging
from pathlib import Path

from epic_app.externals.external_runner_protocol import ExternalRunnerProtocol


class ExternalRunnerLogging:
    _runner: ExternalRunnerProtocol
    _log_file: Path
    _file_handler: logging.FileHandler

    def __init__(self, runner: ExternalRunnerProtocol) -> None:
        self._runner = runner
        _runner_name = self._get_runner_name()
        self._log_file = self._initialize_log_file(
            runner.output_dir / f"{_runner_name}.log"
        )
        self._file_handler = self._initialize_file_handler(self._log_file)

    def _get_runner_name(self) -> str:
        return type(self._runner).__name__

    def _wrap_message(self, message: str) -> None:
        _decorator = "================================="
        logging.info(_decorator)
        logging.info(message)
        logging.info(_decorator)

    def _initialize_log_file(self, log_file: Path) -> Path:
        if not log_file.is_file():
            log_file.touch()
        return log_file

    def _initialize_file_handler(self, log_file: Path) -> logging.FileHandler:
        _logger = logging.getLogger("")
        _logger.setLevel(logging.INFO)
        _file_handler = logging.FileHandler(filename=log_file, mode="w")
        _file_handler.setLevel(logging.INFO)
        _logger.addHandler(_file_handler)
        self._set_formatter(_file_handler)
        return _file_handler

    def _set_formatter(self, file_handler: logging.FileHandler) -> None:
        # Create a formatter and add to the file and console handlers.
        _formatter = logging.Formatter(
            fmt="%(asctime)s - [%(filename)s:%(lineno)d] - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %I:%M:%S %p",
        )
        file_handler.setFormatter(_formatter)

    def __enter__(self) -> None:
        _runner_name = self._get_runner_name()

        self._wrap_message(f"Initialized Runner Logging for {_runner_name}")

    def __exit__(self, *args, **kwargs) -> None:
        _logger = logging.getLogger("")
        _runner_name = self._get_runner_name()
        self._wrap_message(f"Logger terminated for {_runner_name}")
        _logger.removeHandler(self._file_handler)
