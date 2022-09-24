from typing import Callable, Type

import pytest

from epic_app.externals.ERAMVisuals.eram_visuals_runner_base import (
    EramVisualsRunnerBase,
)
from epic_app.externals.ERAMVisuals.eram_visuals_runner_factory import (
    EramVisualsRunnerFactory,
)
from epic_app.externals.ERAMVisuals.eram_visuals_runner_unix import (
    EramVisualsRunnerUnix,
)
from epic_app.externals.ERAMVisuals.eram_visuals_runner_windows import (
    EramVisualsRunnerWindows,
)


class TestEramVisualsRunnerFactory:
    def test_get_runner_unknown_platform_raises(self):
        _unknown_platform = "Unknown"
        _expected_err = f"No runner available for platform {_unknown_platform}"
        with pytest.raises(NotImplementedError) as exc_err:
            EramVisualsRunnerFactory.get_runner("Unknown")
        assert str(exc_err.value) == _expected_err

    @pytest.mark.parametrize(
        "platform_name, expected_runner",
        [
            pytest.param("Windows", EramVisualsRunnerWindows, id="Windows Runner"),
            pytest.param("Linux", EramVisualsRunnerUnix, id="Unix Runner"),
        ],
    )
    @pytest.mark.parametrize(
        "modify_name",
        [
            pytest.param(lambda x: x.lower(), id="Lowercase"),
            pytest.param(lambda x: x.upper(), id="Uppercase"),
            pytest.param(lambda x: x.capitalize(), id="Capitalize"),
            pytest.param(lambda x: x, id="As is"),
        ],
    )
    def test_get_runner_given_known_platform_returns_expected_runner(
        self,
        platform_name: str,
        expected_runner: Type[EramVisualsRunnerBase],
        modify_name: Callable,
    ):
        _platform_name = modify_name(platform_name)
        _found_runner = EramVisualsRunnerFactory.get_runner(_platform_name)
        assert _found_runner == expected_runner
