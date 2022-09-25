from typing import Any

import pytest

from epic_app.externals.subprocess_try_hard_runner import (
    ExternalScriptArguments,
    SubprocessTryHardRunner,
)


class TestSubprocessTryHardRunner:
    def test_initialize_subprocesstryhardrunner(self):
        _runner = SubprocessTryHardRunner()
        assert _runner

    def test_given_missing_r_script_tries_again(self, request: pytest.FixtureRequest):
        # 1. Define test data.
        class MockTryHardRunner(SubprocessTryHardRunner):
            def _run_with(self, _subprocess_call: Any) -> None:
                if not _subprocess_call:
                    raise ValueError()

        class MockExternalScriptArguments(ExternalScriptArguments):
            def __init__(self) -> None:
                super().__init__()
                self._as_main_call = 0
                self._as_fallback_call = 0

            def as_main_call(self) -> None:
                self._as_main_call += 1
                return None

            def as_fallback_call(self) -> None:
                self._as_fallback_call += 1
                return "sth"

        _runner = MockTryHardRunner()
        assert isinstance(_runner, SubprocessTryHardRunner)

        # 2. Run mocked up test
        _arguments = MockExternalScriptArguments()
        _runner.run(_arguments)

        # 3. Verify final expectations
        assert _arguments._as_main_call == 1
        assert _arguments._as_fallback_call == 1
