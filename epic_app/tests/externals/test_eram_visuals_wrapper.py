from epic_app.tests import test_data_dir
from epic_app.tests.epic_db_fixture import epic_test_db


class TestSummaryEvolutionGraph:
    def test_execute_r_snippet(self):
        # 1. Define test data.
        _csv_file = test_data_dir / "csv" / "evo_summary.csv"
        assert _csv_file.is_file()
        _png_file = test_data_dir / "test_evo_summary.png"
        if _png_file.is_file():
            _png_file.unlink()
        if _png_file.with_suffix(".pdf").exists():
            _png_file.unlink()

        # 2. Run test.
        # SummaryEvolutionGraph.execute_r_snippet(_csv_file, _png_file)

        # 3. Verify final expectations.
        assert _png_file.exists()
        assert _png_file.with_suffix(".pdf").exists()
