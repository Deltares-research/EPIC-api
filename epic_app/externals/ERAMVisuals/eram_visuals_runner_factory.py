from epic_app.exporters.ERAMVisuals.eram_Visuals_runner_unix import (
    EramVisualsRunnerUnix,
)
from epic_app.exporters.ERAMVisuals.eram_Visuals_runner_windows import (
    EramVisualsRunnerWindows,
)
from epic_app.externals.ERAMVisuals.eram_visuals_runner import EramVisualsRunnerBase


class EramVisualsRunnerFactory:
    @staticmethod
    def get_runner(platform: str) -> EramVisualsRunnerBase:
        """
        Gets the appropiate runner based on the platform Django is running on.

        Returns:
            EramVisualsRunner: Runner suitable for the platform.
        """
        _available_runners: List[EramVisualsRunnerBase] = [
            EramVisualsRunnerWindows,
            EramVisualsRunnerUnix,
        ]
        _elegible_runners = [
            runner for runner in _available_runners if runner.can_run(platform)
        ]
        if not _elegible_runners:
            raise NotImplementedError(
                "No runner available for platform {}".format(platform)
            )
        if len(_elegible_runners) > 1:
            raise ValueError("No more than one runner should be elegible.")
        return _elegible_runners[0]
