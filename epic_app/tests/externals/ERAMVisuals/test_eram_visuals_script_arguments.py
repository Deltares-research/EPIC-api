import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, List

import pytest
from genericpath import exists

from epic_app.externals.ERAMVisuals.eram_visuals_runner import (
    EramVisualsScriptArguments,
)
from epic_app.tests import test_data_dir


class TestEramVisualsScriptArguments:
    csv_test_cases = [
        pytest.param("evo_summary.csv", id="ERAM Visual Sample data"),
        # pytest.param("evolution_empty_summary.csv", id="EPIC Generated sample data"),
    ]
    call_args_test_cases = [
        pytest.param(
            lambda x: x.main_call.as_main_call(), id="Main Call - as main call"
        ),
        pytest.param(
            lambda x: x.main_call.as_fallback_call(),
            id="Main Call - as fallback call",
        ),
        pytest.param(
            lambda x: x.fallback_call.as_main_call(),
            id="Fallback Call - as main call",
        ),
        pytest.param(
            lambda x: x.fallback_call.as_fallback_call(),
            id="Fallback Call - as fallback call",
        ),
    ]

    @pytest.mark.parametrize("test_file", csv_test_cases)
    @pytest.mark.parametrize("with_args", call_args_test_cases)
    def test_run_subprocess_with_eram_Visuals_script_arguments(
        self, test_file: str, with_args: Callable, request: pytest.FixtureRequest
    ):
        # 1. Define test data.
        _csv_file = test_data_dir / "csv" / test_file
        assert _csv_file.exists()
        _test_case_name = (
            request.node.name.replace(" ", "_").replace("[", "__").replace("]", "__")
        )
        _output_dir = test_data_dir / type(self).__name__ / _test_case_name
        shutil.rmtree(_output_dir, ignore_errors=True)
        _output_dir.mkdir(parents=True)
        _expected_file = _output_dir / "eram_visuals"

        _eram_args = EramVisualsScriptArguments(_csv_file, _output_dir)
        assert _eram_args
        assert _eram_args.main_call
        assert _eram_args.fallback_call

        # 2. Run test
        _call_args = with_args(_eram_args)
        _return_output = subprocess.run(
            _call_args, shell=True, capture_output=True, text=True
        )

        # 3. Verify final expectations.
        assert _return_output.returncode == 0, _return_output.stdout
        assert _output_dir.is_dir()
        assert _expected_file.with_suffix(".png").is_file()
        assert _expected_file.with_suffix(".pdf").is_file()
