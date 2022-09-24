from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from symbol import decorator

from epic_app.externals.external_runner_protocol import ExternalRunnerProtocol


class ExternalRunnerLogging:
    _runner: ExternalRunnerProtocol
    _log_file: Path
    _file_handler: logging.FileHandler

    def __init__(self, runner: ExternalRunnerProtocol) -> None:
        self._runner = runner
        self._log_file = self._initialize_log_file(runner.output_dir / f"{runner}.log")
        self._file_handler = self._initialize_file_handler(self._log_file)
        self._wrap_message(f"Initialized Runner Logging for {runner}")

    def _wrap_message(self, message: str) -> None:
        _decorator = "================================="
        logging.info(f"{_decorator}\n\n\n")
        logging.info(message)
        logging.info(f"\n\n\n{_decorator}")

    def _initialize_log_file(self, log_file: Path) -> Path:
        if not log_file.is_file():
            log_file.touch()
        return log_file

    def _initialize_file_handler(self, log_file: Path) -> logging.FileHandler:
        _logger = logging.getLogger("")
        _logger.setLevel(logging.INFO)
        _file_handler = logging.FileHandler(filename=log_file, mode="w")
        _file_handler.setLevel(logging.INFO)
        _logger.addHandler(self._file_handler)
        self._set_formatter()
        return _file_handler

    def _set_formatter(self) -> None:
        # Create a formatter and add to the file and console handlers.
        _formatter = logging.Formatter(
            fmt="%(asctime)s - [%(filename)s:%(lineno)d] - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %I:%M:%S %p",
        )
        self._file_handler.setFormatter(_formatter)

    def __del__(self) -> None:
        _logger = logging.getLogger("")
        self._wrap_message(f"Logger terminated for {self._runner}")
        _logger.removeHandler(self._file_handler)
