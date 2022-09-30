import shutil
from pathlib import Path

import pytest

from epic_app.externals.ERAMVisuals.eram_visuals_wrapper import (
    EramVisualsRunner,
    EramVisualsWrapper,
)
from epic_app.externals.external_wrapper_base import (
    ExternalRunner,
    ExternalWrapperStatusType,
)
from epic_app.tests import test_data_dir


def _csv_file_as_pytest_param(csv_file: Path) -> pytest.param:
    _case_id = csv_file.stem.replace("__", ".").replace("_", " ").capitalize()
    return pytest.param(csv_file, id=_case_id)


csv_cases = list(
    map(
        _csv_file_as_pytest_param,
        (test_data_dir / "evolution_summary_examples").glob("*.csv"),
    )
)


class TestEramVisualsWrapper:
    @pytest.mark.parametrize(
        "csv_file",
        csv_cases,
    )
    def test_execute_r_snippet_with_sample_data_succeeds(
        self, csv_file: Path, request: pytest.FixtureRequest
    ):
        # 1. Define test data.
        assert csv_file.exists()
        _test_case_name = (
            request.node.name.replace(" ", "_").replace("[", "__").replace("]", "__")
        )
        _output_dir = test_data_dir / _test_case_name
        shutil.rmtree(_output_dir, ignore_errors=True)

        # 2. Run test.
        eram_visuals = EramVisualsWrapper(
            input_file=csv_file, output_dir=_output_dir, runner=EramVisualsRunner
        )
        eram_visuals.execute()

        # 3. Verify final expectations.
        assert eram_visuals.status.status_type == ExternalWrapperStatusType.SUCCEEDED
        assert eram_visuals.output
        assert eram_visuals.output.png_output.parent == _output_dir
        assert eram_visuals.output.pdf_output.parent == _output_dir
        assert eram_visuals.output.png_output.exists()
        assert eram_visuals.output.pdf_output.exists()

    @pytest.mark.parametrize(
        "csv_file",
        csv_cases,
    )
    def test_execute_r_snippet_with_data_and_spaces_after_comma_succeeds(
        self, csv_file: Path, request: pytest.FixtureRequest
    ):
        # 1. Define test data.
        assert csv_file.exists()
        _test_case_name = (
            request.node.name.replace(" ", "_").replace("[", "__").replace("]", "__")
        )
        _output_dir = test_data_dir / _test_case_name
        shutil.rmtree(_output_dir, ignore_errors=True)
        _output_dir.mkdir(parents=True)

        # 2. Modfiy file and run test.
        _new_lines = csv_file.read_text().replace(",", " , ")
        _csv_modified_file = _output_dir / f"modified_{csv_file.name}"
        _csv_modified_file.write_text(_new_lines)

        eram_visuals = EramVisualsWrapper(
            input_file=_csv_modified_file,
            output_dir=_output_dir,
            runner=EramVisualsRunner,
        )
        eram_visuals.execute()

        # 3. Verify final expectations.
        assert eram_visuals.status.status_type == ExternalWrapperStatusType.SUCCEEDED
        assert eram_visuals.output
        assert eram_visuals.output.png_output.parent == _output_dir
        assert eram_visuals.output.pdf_output.parent == _output_dir
        assert eram_visuals.output.png_output.exists()
        assert eram_visuals.output.pdf_output.exists()

    def test_given_failed_execute_status_is_failed(
        self, request: pytest.FixtureRequest
    ):
        _exception_mssg = "Ea aliqua culpa occaecat minim reprehenderit et."

        class MockEramRunner(ExternalRunner):
            def run(self, *args, **kwargs) -> None:
                raise Exception(_exception_mssg)

        # 1. Define test data.
        _output_dir = test_data_dir / request.node.name
        if _output_dir.exists():
            shutil.rmtree(_output_dir)
        _csv_file = test_data_dir / "csv" / "evo_summary.csv"

        # 2. Run mocked up test
        _test_wrapper = EramVisualsWrapper(
            input_file=_csv_file, output_dir=_output_dir, runner=MockEramRunner
        )
        _test_wrapper.execute()

        # 3. Verify final expectations
        assert _test_wrapper.status.status_type == ExternalWrapperStatusType.FAILED
        assert _test_wrapper.status.status_info == _exception_mssg
        assert str(_test_wrapper.status) == f"Failed: {_exception_mssg}"
        assert _test_wrapper.output
        assert not _test_wrapper.output.pdf_output.exists()
        assert not _test_wrapper.output.png_output.exists()

    def test_given_missing_r_script_tries_again(self, request: pytest.FixtureRequest):
        class MockEramRunner(EramVisualsRunner):
            def _get_platform_runner(self) -> None:
                raise NotImplementedError

        # 1. Define test data.
        _output_dir = test_data_dir / request.node.name
        if _output_dir.exists():
            shutil.rmtree(_output_dir)
        _csv_file = test_data_dir / "csv" / "evo_summary.csv"

        # 2. Run mocked up test
        _test_wrapper = EramVisualsWrapper(
            input_file=_csv_file, output_dir=_output_dir, runner=MockEramRunner
        )
        _test_wrapper.execute()

        # 3. Verify final expectations
        assert _test_wrapper.status.status_type == ExternalWrapperStatusType.SUCCEEDED
        assert _test_wrapper.output
        assert _test_wrapper.output.png_output.exists()
        assert _test_wrapper.output.pdf_output.exists()
