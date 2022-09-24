from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from epic_app.externals.external_runner_protocol import ExternalRunnerProtocol


class ExternalRunnerLogging:
    _runner: ExternalRunnerProtocol
    _log_file: Path
    _file_handler: logging.FileHandler

    def __init__(self, runner: ExternalRunnerProtocol) -> None:
        self._runner = runner
        self._log_file = self._initialize_log_file(runner.output_dir / f"{runner}.log")
        self._file_handler = self._initialize_file_handler(self._log_file)
        logging.info(
            f"---Initialized Runner Logging for {runner} at {datetime.now()}---"
        )

    def _initialize_log_file(self, log_file: Path) -> Path:
        log_file.unlink(missing_ok=True)
        log_file.touch()
        return log_file

    def _initialize_file_handler(self, log_file: Path) -> logging.FileHandler:
        _logger = logging.getLogger("")
        _logger.setLevel(logging.INFO)
        _file_handler = logging.FileHandler(filename=log_file, mode="w")
        _file_handler.setLevel(logging.INFO)
        _logger.addHandler(self._file_handler)
        return _file_handler

    def __del__(self) -> None:
        _logger = logging.getLogger("")
        logging.info(f"Terminating {self._runner} logger {datetime.now()}")
        _logger.removeHandler(self._file_handler)
