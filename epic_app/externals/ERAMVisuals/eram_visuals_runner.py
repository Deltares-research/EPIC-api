from __future__ import annotations

import logging
import subprocess
from os import environ
from pathlib import Path
from typing import List, Union

from epic_app.externals.ERAMVisuals import eram_visuals_script
from epic_app.externals.external_runner_logging import ExternalRunnerLogging
from epic_app.externals.external_runner_protocol import ExternalRunnerProtocol
from epic_app.externals.subprocess_try_hard_runner import (
    ExternalScriptArguments,
    SubprocessTryHardRunner,
)


class EramVisualsScriptArguments(ExternalScriptArguments):
    def __init__(
        self,
        main_call: Path,
        fallback_call: Union[Path, str],
        csv_input: Path,
        output_dir: Path,
    ) -> None:
        self._main_call = main_call
        self._fallback_call = fallback_call
        self._csv_input = csv_input
        self._output_dir = output_dir
        self._eram_visuals = eram_visuals_script

    def as_main_call(self) -> List[Union[Path, str]]:
        return [
            self._main_call,
            self._eram_visuals,
            self._csv_input,
            self._output_dir,
            "--verbose",
        ]

    def as_fallback_call(self) -> List[Union[Path, str]]:
        return [
            self._fallback_call,
            self._eram_visuals,
            self._csv_input,
            self._output_dir,
            "--verbose",
        ]


class EramVisualsScriptArgumentsUnified(EramVisualsScriptArguments):
    def as_main_call(self) -> List[Union[Path, str]]:
        return [" ".join(super().as_main_call())]

    def as_fallback_call(self) -> List[Union[Path, str]]:
        return [" ".join(super().as_fallback_call())]


class EramVisualsRunner(ExternalRunnerProtocol):
    def run(self, *args, **kwargs) -> None:
        assert eram_visuals_script.exists()
        _output_dir = kwargs["output_dir"]
        with ExternalRunnerLogging(self, _output_dir):
            _try_hard_runner = SubprocessTryHardRunner()
            try:
                _try_hard_runner.run(
                    EramVisualsScriptArguments(
                        self._get_platform_runner(),
                        "Rscript",
                        kwargs["input_file"],
                        _output_dir,
                    )
                )
            except Exception as first_try_exc:
                logging.info(f"Fallback run triggered due to exception {first_try_exc}")
                _try_hard_runner.run(
                    EramVisualsScriptArgumentsUnified(
                        self._get_platform_runner(),
                        "Rscript",
                        kwargs["input_file"],
                        _output_dir,
                    )
                )

    def _run_with(
        self, r_script_bin: Union[Path, str], eram_args: EramVisualsScriptArguments
    ) -> None:
        _subprocess_call = eram_args.as_subprocess_call(r_script_bin)
        _command_str = " ".join(_subprocess_call)
        logging.info(f"Running command: {_command_str}")
        _return_output = subprocess.run(
            _subprocess_call, shell=True, capture_output=True, text=True
        )
        logging.info(f"Output run: {_return_output.stdout}")
        if _return_output.returncode != 0:
            _call_err = f"Execution failed with code {_return_output.returncode}. Error log: {_return_output.stderr}"
            logging.error(_call_err)
            raise ValueError(_call_err)

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
