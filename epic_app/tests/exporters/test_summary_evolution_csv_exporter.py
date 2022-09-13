import shutil
from typing import Union

import pytest

from epic_app.exporters.summary_evolution_csv_exporter import (
    SummaryEvolutionCsvFile,
    SummaryEvolutionCsvRow,
)
from epic_app.tests import test_data_dir


class TestSummaryEvolutionCsvRow:
    @pytest.mark.parametrize(
        "average_value",
        [
            pytest.param("4,2", id="As str with comma"),
            pytest.param("4.2", id="As str with point"),
            pytest.param(4.2, id="As float"),
        ],
    )
    def test_value_from_serialized_data(self, average_value: Union[str, float]):
        # 1. Given: define test data.
        _area_value = "Ut sint incididunt ut minim aliqua non culpa quis anim aliquip nostrud ullamco dolore officia."
        _group_value = (
            "Proident sit magna aute laborum adipisicing non minim consectetur ea duis."
        )
        _program_value = "Ex fugiat magna est non commodo qui fugiat adipisicing."
        # 2. When: run test.
        _csv_row = SummaryEvolutionCsvRow.from_serialized_data(
            dict(
                area=_area_value,
                group=_group_value,
                program=_program_value,
                average=average_value,
            )
        )

        # 3. Then: validate expectations.
        assert _csv_row
        assert _csv_row.group == _area_value[0]
        assert _csv_row.sub == _group_value
        assert _csv_row.individual == _program_value
        assert _csv_row.value == "4.2"

    def test_sub_and_individual_from_serialized_data(self):
        # 1. Given: define test data.
        _area_value = "Ut sint incididunt ut minim aliqua non culpa quis anim aliquip nostrud ullamco dolore officia."
        _str_with_commas = "Just, a, value"
        _expected_result = "Just  a  value"
        # 2. When: run test.
        _csv_row = SummaryEvolutionCsvRow.from_serialized_data(
            dict(
                area=_area_value,
                group=_str_with_commas,
                program=_str_with_commas,
                average=4.2,
            )
        )

        # 3. Then: validate expectations.
        assert _csv_row
        assert _csv_row.group == _area_value[0]
        assert _csv_row.sub == _expected_result
        assert _csv_row.individual == _expected_result
        assert _csv_row.value == "4.2"

    def test_to_string(self):
        # 1. Given: define test data.
        _csv_row = SummaryEvolutionCsvRow()
        _csv_row.group = "Adipisicing aliquip sunt exercitation dolore ad ipsum id occaecat eiusmod veniam."
        _csv_row.sub = "Magna qui cupidatat ex sunt ea non fugiat aliquip quis eu culpa fugiat sit dolore."
        _csv_row.individual = "Nulla aliqua tempor proident aliqua labore consequat labore consequat et irure pariatur."
        _csv_row.value = "Adipisicing reprehenderit ad cillum excepteur fugiat dolor dolore consectetur est non dolor."

        # 2. When: run test.
        _as_str = _csv_row.to_string()

        # 3. Then: validate expectations.
        assert (
            _as_str
            == f"{_csv_row.group}, {_csv_row.sub}, {_csv_row.individual}, {_csv_row.value}"
        )

    def test_get_headers(self):
        assert SummaryEvolutionCsvRow.get_headers() == "group, sub, individual, value"


class TestSummaryEvolutionCsvExporter:
    def test_given_valid_data_exports_to_csv(self, request: pytest.FixtureRequest):
        # 1. Given. Define test data.
        _row = SummaryEvolutionCsvRow.from_serialized_data(
            dict(
                area="A group",
                group="A sub",
                program="An individual",
                average="A value",
            )
        )
        _test_data_dir = test_data_dir / request.node.name
        if _test_data_dir.is_dir():
            shutil.rmtree(_test_data_dir)

        # 2. When. Run test
        _exporter = SummaryEvolutionCsvFile()
        _exporter.rows = [_row]
        _generated_csv = _exporter.export(_test_data_dir)

        # 3. Then. Verify final expectations.
        assert _generated_csv.is_file()

    def test_given_empty_valid_data_exports_to_csv(
        self, request: pytest.FixtureRequest
    ):
        # 1. Given. Define test data.
        _test_data_dir = test_data_dir / request.node.name
        if _test_data_dir.is_dir():
            shutil.rmtree(_test_data_dir)

        # 2. When. Run test
        _exporter = SummaryEvolutionCsvFile()
        _exporter.rows = []
        _generated_csv = _exporter.export(_test_data_dir)

        # 3. Then. Verify final expectations.
        assert _generated_csv.is_file()
