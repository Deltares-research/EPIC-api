import shutil

import pytest

from epic_app.externals.ERAMVisuals.eram_visuals_runner_windows import (
    EramVisualsRunnerWindows,
)
from epic_app.tests import test_data_dir


class TestEramVisualsRunnerWindows:
    @pytest.mark.parametrize(
        "test_file",
        [
            pytest.param("evo_summary.csv", id="ERAM Visual Sample data"),
            pytest.param(
                "evolution_empty_summary.csv", id="EPIC Generated sample data"
            ),
        ],
    )
    def test_execute_r_snippet_with_sample_data_succeeds(
        self, test_file: str, request: pytest.FixtureRequest
    ):
        # 1. Define test data.
        _csv_file = test_data_dir / "csv" / test_file
        _output_dir = test_data_dir / type(self).__name__ / request.node.name
        shutil.rmtree(_output_dir, ignore_errors=True)
        _output_dir.mkdir(parents=True)
        _expected_file = _output_dir / "eram_visuals"
        # 2. Run test
        EramVisualsRunnerWindows().run(output_dir=_output_dir, input_file=_csv_file)

        # 3. Verify final expectations
        assert _output_dir.is_dir()
        assert _expected_file.with_suffix(".png").exists()
        assert _expected_file.with_suffix(".pdf").exists()
        _log_file = next(_output_dir.glob("*.log"), None)
        assert _log_file
