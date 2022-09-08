from epic_app.externals.eram_visuals_wrapper import EramVisualsWrapper
from epic_app.externals.external_wrapper_base import ExternalWrapperStatusType
from epic_app.tests import test_data_dir


class TestSummaryEvolutionGraph:
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
        eram_visuals = EramVisualsWrapper()
        eram_visuals.execute(dict(input_file=_csv_file, output_file=_png_file))

        # 3. Verify final expectations.
        assert eram_visuals.status.status_type == ExternalWrapperStatusType.SUCCEEDED
        assert _png_file.exists()
        assert _png_file.with_suffix(".pdf").exists()
