from __future__ import annotations

from pathlib import Path
from typing import List, Protocol, Union


class TryHardScriptCallProtocol(Protocol):
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
        pass


class TryHardScriptArgumentsProtocol(Protocol):
    main_call: TryHardScriptCallProtocol
    fallback_call: TryHardScriptCallProtocol

    