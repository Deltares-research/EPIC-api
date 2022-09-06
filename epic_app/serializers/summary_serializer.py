from typing import List

from rest_framework import serializers

from epic_app.models.epic_answers import (
    AgreementAnswerType,
    EvolutionAnswer,
    MultipleChoiceAnswer,
)
from epic_app.models.epic_questions import (
    EvolutionChoiceType,
    EvolutionQuestion,
    LinkagesQuestion,
)
from epic_app.models.epic_user import EpicOrganization


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
            "id": instance.program.name,
            "name": instance.program.name,
            "selected_programs": _answers_summary,
        }


class SummaryEvolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvolutionQuestion
        fields = "__all__"

    def to_representation(self, instance: EvolutionQuestion):
        organization_users = self.context["users"].all()
        user_ids = [eu.id for eu in organization_users]
        _query = EvolutionAnswer.objects.filter(
            user__in=user_ids, question=instance
        ).all()

        def avg_answers(answers_list: List[EvolutionAnswer]) -> int:
            answers_as_int = map(EvolutionChoiceType.to_int, answers_list)
            answers_avg = sum(answers_as_int) / len(answers_list)
            return min(round(answers_avg, 0), len(EvolutionChoiceType.as_list()))

        _answers_summary = int(
            avg_answers(_query.values_list("selected_choice", flat=True))
        )

        return {
            "id": instance.pk,
            "title": instance.title,
            "average": _answers_summary,
        }


class SummaryOrganizationEvolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EpicOrganization
        fields = "__all__"

    def to_representation(self, instance: EpicOrganization):
        _answers_summary = SummaryEvolutionSerializer(
            EvolutionQuestion.objects.all(),
            many=True,
            context={"request": self.context, "users": instance.organization_users},
        ).data

        return {
            "id": instance.pk,
            "organization": instance.name,
            "evolution_questions": _answers_summary,
        }
