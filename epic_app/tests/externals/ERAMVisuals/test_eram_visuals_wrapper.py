import shutil
from unittest.mock import Mock

import pytest

from epic_app.externals.ERAMVisuals.eram_visuals_wrapper import (
    EramVisualsOutput,
    EramVisualsWrapper,
)
from epic_app.externals.external_wrapper_base import (
    ExternalRunner,
    ExternalWrapperStatusType,
)
from epic_app.tests import test_data_dir


class TestEramVisualsWrapper:
    def test_execute_r_snippet_with_sample_data_succeeds(
        self, request: pytest.FixtureRequest
    ):
        # 1. Define test data.
        _csv_file = test_data_dir / "csv" / "evo_summary.csv"
        assert _csv_file.exists()
        _output_dir = test_data_dir / request.node.name
        if _output_dir.exists():
            shutil.rmtree(_output_dir)

        # 2. Run test.
        eram_visuals = EramVisualsWrapper(input_file=_csv_file, output_dir=_output_dir)
        eram_visuals.execute()

        # 3. Verify final expectations.
        assert eram_visuals.status.status_type == ExternalWrapperStatusType.SUCCEEDED
        assert eram_visuals.output
        assert eram_visuals.output.png_output.exists()
        assert eram_visuals.output.pdf_output.exists()

    def test_given_failed_execute_status_is_failed(
        self, request: pytest.FixtureRequest
    ):
        _exception_mssg = "Ea aliqua culpa occaecat minim reprehenderit et."

        class MockEramRunner(ExternalRunner):
            def run(self, *args, **kwargs) -> None:
                raise Exception(_exception_mssg)

        class MockEramVisualWrapper(EramVisualsWrapper):
            @property
            def runner(self) -> ExternalRunner:
                return MockEramRunner()

        # 1. Define test data.
        _output_dir = test_data_dir / request.node.name
        if _output_dir.exists():
            shutil.rmtree(_output_dir)
        _csv_file = test_data_dir / "csv" / "evo_summary.csv"

        # 2. Run mocked up test
        _test_wrapper = MockEramVisualWrapper(
            input_file=_csv_file, output_dir=_output_dir
        )
        _test_wrapper.execute()

        # 3. Verify final expectations
        assert _test_wrapper.status.status_type == ExternalWrapperStatusType.FAILED
        assert _test_wrapper.status.status_info == _exception_mssg
        assert str(_test_wrapper.status) == f"Failed: {_exception_mssg}"
        assert _test_wrapper.output
        assert not _test_wrapper.output.pdf_output.exists()
        assert not _test_wrapper.output.png_output.exists()
