from typing import Any, List, Optional

from rest_framework import serializers

from epic_app.models.epic_answers import EvolutionAnswer, MultipleChoiceAnswer
from epic_app.models.epic_questions import EvolutionChoiceType, LinkagesQuestion
from epic_app.models.epic_user import EpicOrganization, EpicUser
from epic_app.models.models import Program


class SummaryLinkagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkagesQuestion
        fields = "__all__"

    def to_representation(self, instance: LinkagesQuestion):
        organization_users = self.context["users"].all()
        user_ids = [eu.id for eu in organization_users]
        _query = MultipleChoiceAnswer.objects.filter(
            user__in=user_ids, question=instance
        ).all()
        _answers_summary = list(set(_query.values_list("selected_programs", flat=True)))

        return {
            "id": instance.program.pk,
            "name": instance.program.name,
            "selected_programs": _answers_summary,
        }


class SummaryEvolutionSerializer(serializers.ModelSerializer):
    """
    - Avg(ResponsesOrganization(Avg(ResponseUsers))
    - Each user averages their total evolution answers.
    - For every organization the total evolution answers got averaged for all users.
    """

    class Meta:
        model = Program
        fields = "__all__"

    def _get_average(self, list_items: List[Any]) -> Optional[float]:
        if not list_items:
            return None
        return sum(list_items) / len(list_items)

    def _get_user_average_evolution_program(
        self, org_user: EpicUser, program: Program
    ) -> Optional[float]:
        _answers = EvolutionAnswer.objects.filter(
            user=org_user, question__in=program.questions.all()
        ).values_list("selected_choice", flat=True)
        _int_answers = []
        for _ans in _answers:
            _answer_as_int = EvolutionChoiceType.to_int(_ans)
            if _answer_as_int is not None:
                _int_answers.append(_answer_as_int)
        if not _int_answers:
            return None
        return self._get_average(_int_answers)

    def _get_organization_average_evolution_program(
        self, epic_org: EpicOrganization, program: Program
    ) -> Optional[float]:
        avg_list = []
        _users = epic_org.organization_users.all()
        if not _users:
            return None
        for epic_user in _users:
            _user_average_answers = self._get_user_average_evolution_program(
                epic_user, program
            )
            if _user_average_answers is not None:
                avg_list.append(_user_average_answers)
        return self._get_average(avg_list)

    def to_representation(self, instance: Program):
        _organizations = self.context["organizations"].all()
        _org_averages = [
            self._get_organization_average_evolution_program(epic_org, instance)
            for epic_org in list(_organizations)
        ]
        _org_averages = [_org_avg for _org_avg in _org_averages if _org_avg is not None]
        _answers_summary = 0
        if _org_averages:
            _answers_summary = round(self._get_average(_org_averages), 2)
        return {
            "id": instance.pk,
            "area": instance.group.area.name,
            "group": instance.group.name,
            "program": instance.name,
            "average": _answers_summary,
        }


class SummaryOrganizationEvolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpicOrganization
        fields = "__all__"

    def to_representation(self, instance: EpicOrganization):
        _answers_summary = SummaryEvolutionSerializer(
            Program.objects.all(),
            many=True,
            context={
                "request": self.context,
                "organizations": EpicOrganization.objects.filter(pk=instance.pk),
            },
        ).data

        return {
            "id": instance.pk,
            "organization": instance.name,
            "evolution_summary": _answers_summary,
        }
