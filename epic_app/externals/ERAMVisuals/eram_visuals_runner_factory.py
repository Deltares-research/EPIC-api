from typing import List

from epic_app.externals.ERAMVisuals.eram_visuals_runner_base import (
    EramVisualsRunnerBase,
)
from epic_app.externals.ERAMVisuals.eram_visuals_runner_unix import (
    EramVisualsRunnerUnix,
)
from epic_app.externals.ERAMVisuals.eram_visuals_runner_windows import (
    EramVisualsRunnerWindows,
)


class EramVisualsRunnerFactory:
    @staticmethod
    def get_runner(platform: str) -> EramVisualsRunnerBase:
        """
        Gets the appropiate runner based on the platform Django is running on.

        Returns:
            EramVisualsRunner: Runner suitable for the platform.
        """
        _available_runners = dict(
            windows=EramVisualsRunnerWindows, linux=EramVisualsRunnerUnix
        )
        _runner = _available_runners.get(platform.lower(), None)
        if not _runner:
            raise NotImplementedError(
                "No runner available for platform {}".format(platform)
            )

        return _runner
