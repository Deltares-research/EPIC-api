from pathlib import Path

from epic_app.externals.eram_visuals_wrapper import EramVisualsWrapper
from epic_app.externals.external_wrapper_base import ExternalWrapperStatusType
from epic_app.tests import test_data_dir


class TestEramVisualsWrapper:
    def test_execute_r_snippet_with_sample_data_succeeds(self):
        # 1. Define test data.
        _csv_file = test_data_dir / "csv" / "evo_summary.csv"
        assert _csv_file.exists()
        _png_file = test_data_dir / "test_evo_summary.png"
        if _png_file.is_file():
            _png_file.unlink()
        if _png_file.with_suffix(".pdf").is_file():
            _png_file.with_suffix(".pdf").unlink()

        # 2. Run test.
        eram_visuals = EramVisualsWrapper(input_file=_csv_file, output_file=_png_file)
        eram_visuals.execute()

        # 3. Verify final expectations.
        assert eram_visuals.status.status_type == ExternalWrapperStatusType.SUCCEEDED
        assert _png_file.exists()
        assert _png_file.with_suffix(".pdf").exists()

    def test_given_failed_execute_status_is_failed(self):
        _exception_mssg = "Ea aliqua culpa occaecat minim reprehenderit et."

        class MockEramVisualsWrapper(EramVisualsWrapper):
            def _run_script(self) -> None:
                raise Exception(_exception_mssg)

        # 1. Define test data.
        _csv_file = test_data_dir / "csv" / "evo_summary.csv"
        _png_file = test_data_dir / "test_evo_summary.png"

        # 2. Run mocked up test
        _test_wrapper = MockEramVisualsWrapper(
            input_file=_csv_file, output_file=_png_file
        )
        _test_wrapper.execute()

        # 3. Verify final expectations
        assert _test_wrapper.status.status_type == ExternalWrapperStatusType.FAILED
        assert _test_wrapper.status.status_info == _exception_mssg
        assert str(_test_wrapper.status) == f"Failed: {_exception_mssg}"
