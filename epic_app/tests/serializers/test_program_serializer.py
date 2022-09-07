from collections import OrderedDict

import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from epic_app.models.models import Group, Program, ProgramReference
from epic_app.serializers.program_serializer import (
    ProgramReferenceSerializer,
    ProgramSerializer,
    SimpleProgramSerializer,
)
from epic_app.tests.epic_db_fixture import epic_test_db


@pytest.fixture(autouse=False)
def program_serializer_fixture(
    epic_test_db: pytest.fixture,
) -> Program:
    """
    Dummy fixture just to load a default db from dummy_db.

    Args:
        epic_test_db (pytest.fixture): Fixture to load for the whole file tests.
    """
    _group = Group.objects.all().first()
    test_program = Program(
        name="dummy_program",
        description="Just a dummy program",
        group=_group,
    )
    test_program.save()
    ref_a = ProgramReference(
        description="A reference", link="www.areference.com", program=test_program
    )
    ref_b = ProgramReference(
        description="B reference", link="www.breference.com", program=test_program
    )
    ref_a.save()
    ref_b.save()
    return test_program


def get_serializer():
    factory = APIRequestFactory()
    request = factory.get("/")

    return {
        "request": Request(request),
    }


serializer_context = get_serializer()


def _program_ref_as_ordered_dict(program_reference: ProgramReference) -> OrderedDict:
    return OrderedDict(
        [
            ("description", program_reference.description),
            ("link", program_reference.link),
        ]
    )


@pytest.mark.django_db
class TestProgramReferenceSerializer:
    def test_serialize_program_reference(self, program_serializer_fixture: Program):
        _program_reference: ProgramReference = (
            program_serializer_fixture.references.first()
        )
        serialized_data = ProgramReferenceSerializer(
            _program_reference, many=False, context=serializer_context
        ).data
        assert serialized_data == {
            "description": _program_reference.description,
            "link": _program_reference.link,
        }


@pytest.mark.django_db
class TestProgramSerializer:
    def test_serialize_program(self, program_serializer_fixture: Program):
        # 1. Define expectations
        _program_id = program_serializer_fixture.pk
        _url = f"http://testserver/api/program/{_program_id}/"
        _refs = list(
            map(
                _program_ref_as_ordered_dict,
                program_serializer_fixture.references.all(),
            )
        )

        # 2. Run test.
        serialized_data = ProgramSerializer(
            program_serializer_fixture, many=False, context=serializer_context
        ).data

        # 3. Verify final expectations.
        assert serialized_data == {
            "url": _url,
            "id": _program_id,
            "name": program_serializer_fixture.name,
            "description": program_serializer_fixture.description,
            "references": _refs,
            "agencies": [],
            "group": program_serializer_fixture.group.pk,
            "questions": [],
        }


@pytest.mark.django_db
class TestSimpleProgramSerializer:
    def test_serialize_simple_program(self, program_serializer_fixture: Program):
        # 1. Define expectations
        _program_id = program_serializer_fixture.pk
        _url = f"http://testserver/api/program/{_program_id}/"
        _refs = list(
            map(
                _program_ref_as_ordered_dict,
                program_serializer_fixture.references.all(),
            )
        )

        # 2. Run test
        serialized_data = SimpleProgramSerializer(
            program_serializer_fixture, many=False, context=serializer_context
        ).data

        # 3. Verify final expectations
        assert serialized_data == {
            "url": _url,
            "id": _program_id,
            "name": program_serializer_fixture.name,
            "description": program_serializer_fixture.description,
            "references": _refs,
        }
