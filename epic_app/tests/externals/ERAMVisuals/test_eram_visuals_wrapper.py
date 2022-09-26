import shutil

import pytest

from epic_app.externals.ERAMVisuals.eram_visuals_runner import (
    EramVisualsScriptArguments,
)
from epic_app.externals.ERAMVisuals.eram_visuals_wrapper import EramVisualsWrapper
from epic_app.externals.external_runner_protocol import ExternalRunnerProtocol
from epic_app.externals.external_wrapper_status import ExternalWrapperStatusType
from epic_app.tests import test_data_dir


class TestEramVisualsWrapper:

    csv_test_cases = [
        pytest.param("evo_summary.csv", id="ERAM Visual Sample data"),
        pytest.param("evolution_empty_summary.csv", id="EPIC Generated sample data"),
    ]

    @pytest.mark.parametrize("test_file", csv_test_cases)
    def test_execute_r_snippet_with_sample_data_succeeds(
        self, test_file: str, request: pytest.FixtureRequest
    ):
        # 1. Define test data.
        _csv_file = test_data_dir / "csv" / test_file
        assert _csv_file.exists()
        _test_case_name = (
            request.node.name.replace(" ", "_").replace("[", "__").replace("]", "__")
        )
        _output_dir = test_data_dir / type(self).__name__ / _test_case_name
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
        _log_file = next(_output_dir.glob("*.log"), None)
        assert _log_file

    def test_given_failed_execute_status_is_failed(
        self, request: pytest.FixtureRequest
    ):
        _exception_mssg = "Ea aliqua culpa occaecat minim reprehenderit et."

        class MockEramRunner(ExternalRunnerProtocol):
            def run(self, *args, **kwargs) -> None:
                raise Exception(_exception_mssg)

        # 1. Define test data.
        _output_dir = test_data_dir / request.node.name
        if _output_dir.exists():
            shutil.rmtree(_output_dir)
        _csv_file = test_data_dir / "csv" / "evo_summary.csv"

        # 2. Run mocked up test
        _test_wrapper = EramVisualsWrapper(input_file=_csv_file, output_dir=_output_dir)
        _test_wrapper._runner = MockEramRunner()
        _test_wrapper.execute()

        # 3. Verify final expectations
        assert _test_wrapper.status.status_type == ExternalWrapperStatusType.FAILED
        assert _test_wrapper.status.status_info == _exception_mssg
        assert str(_test_wrapper.status) == f"Failed: {_exception_mssg}"
        assert _test_wrapper.output
        assert not _test_wrapper.output.pdf_output.exists()
        assert not _test_wrapper.output.png_output.exists()
