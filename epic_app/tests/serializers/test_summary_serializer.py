import random

import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from epic_app.models.epic_answers import EvolutionAnswer
from epic_app.models.epic_questions import EvolutionChoiceType, EvolutionQuestion
from epic_app.models.epic_user import EpicOrganization, EpicUser
from epic_app.serializers.summary_serializer import (
    SummaryEvolutionSerializer,
    SummaryOrganizationEvolutionSerializer,
)
from epic_app.tests import django_postgresql_db
from epic_app.tests.epic_db_fixture import epic_test_db


@django_postgresql_db
def get_serializer():
    factory = APIRequestFactory()
    request = factory.get("/")

    return {
        "request": Request(request),
        "users": EpicUser.objects.all(),
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
        evo_q = EvolutionQuestion.objects.all().first()
        represented_data = SummaryEvolutionSerializer(
            context=serializer_context
        ).to_representation(evo_q)
        assert set(represented_data.keys()) == set(["id", "title", "average"])
        assert isinstance(represented_data["average"], int)


@django_postgresql_db
class TestSummaryOrganizationEvolutionSerializer:
    def test_summary_organization_evolution_to_representation(self):
        represented_data = SummaryOrganizationEvolutionSerializer(
            context=serializer_context
        ).to_representation(EpicOrganization.objects.all().first())
        assert set(represented_data.keys()) == set(
            ["id", "organization", "evolution_questions"]
        )
        assert isinstance(represented_data["evolution_questions"], list)
        assert isinstance(represented_data["evolution_questions"][0], dict)
