import logging
import subprocess
from typing import Any, List

from epic_app.externals.ERAMVisuals import eram_visuals_script
from epic_app.externals.ERAMVisuals.eram_visuals_runner_base import (
    EramVisualsRunnerBase,
)
from epic_app.externals.external_runner_logging import ExternalRunnerLogging


class EramVisualsRunnerUnix(EramVisualsRunnerBase):
    def run(self, *args, **kwargs) -> None:
        assert eram_visuals_script.exists()
        with ExternalRunnerLogging(self):
            try:
                self._run_with(self._get_command(kwargs))
            except Exception as previous_exception:
                logging.info(
                    f"Fallback run triggered due to exception {previous_exception}"
                )
                self._run_with(self._get_fallback_command(kwargs))

    def _run_with(self, command: List[Any]) -> None:
        _command = " ".join(command)
        logging.info(f"Running command: {_command}")
        _return_call = subprocess.call(_command, shell=True)
        if _return_call != 0:
            _call_err = f"Execution failed with code {_return_call}"
            logging.error(_call_err)
            raise ValueError(_call_err)
