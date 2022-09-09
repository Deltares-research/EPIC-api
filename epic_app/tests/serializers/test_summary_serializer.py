import random
from itertools import count
from statistics import mean

import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from epic_app.models.epic_answers import EvolutionAnswer
from epic_app.models.epic_questions import EvolutionChoiceType, EvolutionQuestion
from epic_app.models.epic_user import EpicOrganization, EpicUser
from epic_app.models.models import Program
from epic_app.serializers.summary_serializer import (
    SummaryEvolutionSerializer,
    SummaryOrganizationEvolutionSerializer,
)
from epic_app.tests import django_postgresql_db, test_data_dir
from epic_app.tests.epic_db_fixture import epic_test_db


@django_postgresql_db
def get_serializer():
    factory = APIRequestFactory()
    request = factory.get("/")

    return {
        "request": Request(request),
        "users": EpicUser.objects.all(),
        "organizations": EpicOrganization.objects.all(),
    }


serializer_context = get_serializer()


@pytest.fixture(autouse=True)
def rest_framework_url_fixture(epic_test_db: pytest.fixture):
    """
    Dummy fixture just to load a default db from dummy_db.

    Args:
        epic_test_db (pytest.fixture): Fixture to load for the whole file tests.
    """

    def set_evolution_values(evo_question: EvolutionQuestion, e_user: EpicUser):
        eva = EvolutionAnswer(question=evo_question, user=e_user)
        eva.save()
        selected = random.choice(range(0, len(EvolutionChoiceType.as_list())))
        eva.selected_choice = EvolutionChoiceType.from_int(selected)
        eva.save()

    for e_user in EpicUser.objects.all():
        for l_question in EvolutionQuestion.objects.all():
            set_evolution_values(l_question, e_user)


@django_postgresql_db
class TestSummaryEvolutionSerializer:
    def test_summary_evolution_to_representation(self):
        # 1. Define test data and expectations.
        test_p: Program = EvolutionQuestion.objects.all().first().program
        org_avg = []
        for e_org in EpicOrganization.objects.all():
            user_avg = []
            for e_user in e_org.organization_users.all():
                _answers = (
                    EvolutionAnswer.objects.filter(
                        user=e_user, question__in=test_p.questions.all()
                    )
                    .all()
                    .values_list("selected_choice", flat=True)
                )
                if not _answers:
                    _answers = [0]
                user_avg.append(mean(list(map(EvolutionChoiceType.to_int, _answers))))
            org_avg.append(mean(user_avg))
        program_avg = round(mean(org_avg), 2)

        # 2. Run test
        represented_data = SummaryEvolutionSerializer(
            context=serializer_context
        ).to_representation(test_p)

        # 3. Verify final expectations.
        assert represented_data == {
            "id": test_p.pk,
            "area": test_p.group.area.name,
            "group": test_p.group.name,
            "program": test_p.name,
            "average": program_avg,
        }

    def test_summary_evolution_with_no_answers_to_representation(self):
        # 1. Define test data and expectations.
        test_p: Program = EvolutionQuestion.objects.all().first().program
        # Remove all answers for the given program
        EvolutionAnswer.objects.filter(question__in=test_p.questions.all()).delete()

        # 2. Run test
        represented_data = SummaryEvolutionSerializer(
            context=serializer_context
        ).to_representation(test_p)

        # 3. Verify final expectations.
        assert represented_data == {
            "id": test_p.pk,
            "area": test_p.group.area.name,
            "group": test_p.group.name,
            "program": test_p.name,
            "average": 0,
        }

    def test_summary_evolution_list(self):
        # 1. Define test data and expectations.
        # 2. Run test
        represented_data = SummaryEvolutionSerializer(
            Program.objects.all(), many=True, context=serializer_context
        ).data

        # 3. Verify final expectations.
        assert represented_data
        assert len(represented_data) == Program.objects.count()
        for json_data in represented_data:
            assert sorted(json_data.keys()) == sorted(
                ["id", "area", "group", "program", "average"]
            )
            _program = Program.objects.get(pk=json_data["id"])
            assert _program.group.area.name == json_data["area"]
            assert _program.group.name == json_data["group"]
            assert _program.name == json_data["program"]
            assert isinstance(json_data["average"], float) or isinstance(
                json_data["average"], int
            )

    def test_summary_evolution_list_with_no_answers(self):
        # 1. Define test data and expectations.
        test_p: Program = EvolutionQuestion.objects.all().first().program
        # Remove all answers for the given program
        EvolutionAnswer.objects.filter(question__in=test_p.questions.all()).delete()

        # 2. Run test
        represented_data = SummaryEvolutionSerializer(
            Program.objects.all(), many=True, context=serializer_context
        ).data

        # 3. Verify final expectations.
        assert represented_data
        assert len(represented_data) == Program.objects.count()
        for json_data in represented_data:
            assert sorted(json_data.keys()) == sorted(
                ["id", "area", "group", "program", "average"]
            )
            _program = Program.objects.get(pk=json_data["id"])
            assert _program.group.area.name == json_data["area"]
            assert _program.group.name == json_data["group"]
            assert _program.name == json_data["program"]
            assert json_data["average"] == 0


@django_postgresql_db
class TestSummaryOrganizationEvolutionSerializer:
    def test_summary_organization_evolution_to_representation(self):
        represented_data = SummaryOrganizationEvolutionSerializer(
            context=serializer_context
        ).to_representation(EpicOrganization.objects.all().first())
        assert set(represented_data.keys()) == set(
            ["id", "organization", "evolution_summary"]
        )
        _evo_summary = represented_data["evolution_summary"]
        assert isinstance(_evo_summary, list)
        assert isinstance(_evo_summary[0], dict)
        assert len(_evo_summary) == Program.objects.count()

    def test_summary_organization_evolution_with_no_answers_to_representation(self):
        # Given Remove all answers for the given program
        EvolutionAnswer.objects.all().delete()

        # When: Run test
        represented_data = SummaryOrganizationEvolutionSerializer(
            context=serializer_context
        ).to_representation(EpicOrganization.objects.all().first())

        # Then: Verify final expectations
        assert set(represented_data.keys()) == set(
            ["id", "organization", "evolution_summary"]
        )
        _evo_summary = represented_data["evolution_summary"]
        assert isinstance(_evo_summary, list)
        assert isinstance(_evo_summary[0], dict)
        assert len(_evo_summary) == Program.objects.count()
