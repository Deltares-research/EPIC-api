import math
from pathlib import Path
from typing import List


class SummaryEvolutionCsvRow:
    group: str
    sub: str
    individual: str
    value: str

    @classmethod
    def from_serialized_data(cls, serialized_data: dict):
        def _with_quotes(column_value: str) -> str:
            return '"' + column_value + '"'

        def get_average(value: float) -> int:
            return str(value).replace(",", ".")

        new_row = cls()
        new_row.group = serialized_data["area"][0]  # only show the first letter
        new_row.sub = _with_quotes(serialized_data["group"])
        new_row.individual = _with_quotes(serialized_data["program"])
        new_row.value = get_average(serialized_data["average"])
        return new_row

    @staticmethod
    def get_headers() -> str:
        return "group, sub, individual, value"

    def to_string(self) -> str:
        return f"{self.group},{self.sub},{self.individual},{self.value}"


class SummaryEvolutionCsvFile:
    rows: List[SummaryEvolutionCsvRow]
    _basename = "evolution_summary.csv"

    @classmethod
    def from_serialized_data(cls, serialized_data: List[dict]):
        _summary = cls()
        _summary.rows = list(
            map(SummaryEvolutionCsvRow.from_serialized_data, serialized_data)
        )
        return _summary

    def _get_rows(self) -> List[SummaryEvolutionCsvRow]:
        from itertools import groupby

        _sorted_rows = sorted(self.rows, key=lambda row: row.group)
        _grouped = []
        for _, result in groupby(_sorted_rows, key=lambda row: row.group):
            _grouped.extend(list(result))
        return _grouped

    def _get_rows_as_str(self) -> str:
        _rows = self._get_rows()
        _rows_as_str = [row.to_string() for row in _rows]
        return "\n".join(_rows_as_str)

    def export(self, export_dir: Path) -> Path:
        if not export_dir.is_dir():
            export_dir.mkdir(parents=True)
        _header = SummaryEvolutionCsvRow.get_headers()
        _rows = self._get_rows_as_str()
        export_file = export_dir / self._basename
        export_file.write_text(_header + "\n" + _rows)
        return export_file
