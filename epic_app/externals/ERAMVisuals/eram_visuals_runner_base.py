import logging
from os import environ
from pathlib import Path
from typing import List

from epic_app.externals.ERAMVisuals import eram_visuals_script
from epic_app.externals.external_runner_protocol import ExternalRunnerProtocol


class EramVisualsRunnerBase(ExternalRunnerProtocol):
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
