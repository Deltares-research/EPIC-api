import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from venv import create

from django.core.files.uploadedfile import InMemoryUploadedFile
from openpyxl import Workbook

from epic_app.importers.xlsx.base_importer import BaseEpicImporter
from epic_app.models.models import Area, Group, Program, ProgramReference


class EpicDomainImporter(BaseEpicImporter):
    """
    Class that contains an importer for all the Epic elements.
    """

    class XlsxLineObject(BaseEpicImporter.XlsxLineObject):
        """
        Maps a XLSX row into a data object that we can better manipulate.
        """

        area: str
        group: str
        program: str
        description: Optional[str]
        reference: Optional[str]
        reference_link: Optional[str]

        @classmethod
        def from_xlsx_row(cls, xlsx_row: Any):
            new_obj = cls()
            new_obj.area = cls.get_valid_cell(xlsx_row, 0)
            new_obj.group = cls.get_valid_cell(xlsx_row, 1)
            new_obj.program = cls.get_valid_cell(xlsx_row, 2)
            new_obj.description = cls.get_valid_cell(xlsx_row, 3)
            new_obj.reference = cls.get_valid_cell(xlsx_row, 4)
            new_obj.reference_link = cls.get_valid_cell(xlsx_row, 5)
            return new_obj

        def _to_program_reference_list(self, to_program: Program) -> None:
            def get_clean_ref(ref_value: str) -> str:
                return ref_value.replace("•\t", "")

            def get_as_list(ref_value_list: str) -> List[str]:
                return [
                    get_clean_ref(ref_value) for ref_value in ref_value_list.split("\n")
                ]

            _references = get_as_list(self.reference)
            _links = get_as_list(self.reference_link)
            for p_reflink in zip(_references, _links):
                _p_ref = ProgramReference(
                    description=p_reflink[0], link=p_reflink[1], program=to_program
                )
                _p_ref.save()

        def to_epic_program(self) -> None:
            epic_area, _ = Area.objects.get_or_create(name=self.area.strip())
            epic_group, _ = Group.objects.get_or_create(
                name=self.group.strip(), area=epic_area
            )
            _created_program = Program(
                name=self.program.strip(),
                description=self.description.strip(),
                group=epic_group,
            )
            _created_program.save()
            self._to_program_reference_list(_created_program)

    def _cleanup_epic_domain(self):
        """
        Dumps the database for the entities to import.
        """
        Area.objects.all().delete()
        Group.objects.all().delete()
        Program.objects.all().delete()

    def import_file(self, input_file: Union[InMemoryUploadedFile, Path]):
        self._cleanup_epic_domain()
        line_objects: List[self.XlsxLineObject] = self._get_xlsx_line_objects(
            input_file
        )
        _headers = line_objects.pop(0)
        list(map(lambda x: x.to_epic_program(), line_objects))
