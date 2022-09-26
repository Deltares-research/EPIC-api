from __future__ import annotations

import logging
import subprocess
from os import environ
from pathlib import Path
from typing import List, Union

from epic_app.externals.ERAMVisuals import eram_visuals_script
from epic_app.externals.external_runner_logging import ExternalRunnerLogging
from epic_app.externals.external_runner_protocol import ExternalRunnerProtocol
from epic_app.externals.subprocess_try_hard_runner import SubprocessTryHardRunner
from epic_app.externals.try_hard_script_arguments_protocol import (
    TryHardScriptArgumentsProtocol,
    TryHardScriptCallProtocol,
)


class EramVisualsScriptArguments(TryHardScriptArgumentsProtocol):
    class MainCall(TryHardScriptCallProtocol):
        def __init__(self, eram_visuals: EramVisualsScriptArguments) -> None:
            self._eram_visuals = eram_visuals

        def as_main_call(self) -> List[Union[Path, str]]:
            _call = [self._eram_visuals._get_main_call_rscript_location()]
            _call.extend(self._eram_visuals._get_arguments())
            return _call

        def as_fallback_call(self) -> List[Union[Path, str]]:
            _call = [self._eram_visuals._get_fallback_call_rscript_location()]
            _call.extend(self._eram_visuals._get_arguments())
            return _call

    class FallbackCall(TryHardScriptCallProtocol):
        def __init__(self, eram_visuals: EramVisualsScriptArguments) -> None:
            self._eram_visuals = eram_visuals

        def as_main_call(self) -> List[str]:
            _call = [self._eram_visuals._get_main_call_rscript_location()]
            _call.extend(self._eram_visuals._get_arguments())
            return " ".join(map(str, _call))

        def as_fallback_call(self) -> List[str]:
            _call = [self._eram_visuals._get_fallback_call_rscript_location()]
            _call.extend(self._eram_visuals._get_arguments())
            return " ".join(map(str, _call))

    main_call: MainCall
    fallback_call: FallbackCall

    def __init__(
        self,
        csv_input: Path,
        output_dir: Path,
    ) -> None:
        assert eram_visuals_script.is_file()
        assert csv_input.is_file()
        self._csv_input = csv_input
        self._output_dir = output_dir
        self.main_call = self.MainCall(self)
        self.fallback_call = self.FallbackCall(self)

    def _get_main_call_rscript_location(self) -> Path:
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

    def _get_fallback_call_rscript_location(self) -> str:
        return "Rscript"

    def _get_arguments(self) -> List[Union[Path, str]]:
        return [
            eram_visuals_script,
            self._csv_input,
            self._output_dir,
            "--verbose",
        ]


class EramVisualsRunner(ExternalRunnerProtocol):
    script_arguments: EramVisualsScriptArguments

    @classmethod
    def with_eram_arguments(
        cls, script_arguments: EramVisualsScriptArguments
    ) -> EramVisualsRunner:
        _runner = cls()
        _runner.script_arguments = script_arguments
        _runner.output_dir = script_arguments._output_dir
        return _runner

    def run(self) -> None:
        with ExternalRunnerLogging(self):
            _try_hard_runner = SubprocessTryHardRunner()
            try:
                _try_hard_runner.run(self.script_arguments.main_call)
            except Exception as first_try_exc:
                logging.info(f"Fallback run triggered due to exception {first_try_exc}")
                _try_hard_runner.run(self.script_arguments.fallback_call)

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
