import logging
import subprocess
from pathlib import Path
from typing import Any, List, Protocol, Union


class ExternalScriptArguments(Protocol):
    def as_main_call(self) -> List[Union[Path, str]]:
        """
        Returns the required arguments for a regular call.

        Returns:
            List[Union[Path, str]]: List of arguments which can be either a Path or a string.
        """
        pass

    def as_fallback_call(self) -> List[Union[Path, str]]:
        """
        Returns the required arguments on a different manner in case the main call fails. Allowing the caller to have a 'fallback' way of executing the script.

        Returns:
            List[Union[Path, str]]: List of arguments which can be either a Path or a string.
        """


class SubprocessTryHardRunner:
    """
    A `subprocess.run` wrapper that will try twice to required call.
    """

    def run(self, external_script_args: ExternalScriptArguments) -> None:
        """
        Tries to run the `subprocess.run` call. If the first time fails then a second call will be done with different arguments.
        If the second call fails the exception will be raised, whilst the first one will only be logged.

        Args:
            external_script_args (ExternalScriptArguments): Data class containing the arguments to include in the `subprocess.run` call.
        """
        try:
            logging.info(f"Trying first run given arguments to subprocess as a list")
            self._run_with(external_script_args.as_main_call())
        except Exception as previous_exception:
            logging.info(
                f"Fallback run triggered due to exception {previous_exception}"
            )
            self._run_with(external_script_args.as_fallback_call())

    def _run_with(self, _subprocess_call: Any) -> None:
        logging.info(f"Running command: {_subprocess_call}")
        _return_output = subprocess.run(
            _subprocess_call, shell=True, capture_output=True, text=True
        )
        logging.info(f"Output run: {_return_output.stdout}")
        if _return_output.returncode != 0:
            _call_err = f"Execution failed with code {_return_output.returncode}. Error log: {_return_output.stderr}"
            logging.error(_call_err)
            raise ValueError(_call_err)
