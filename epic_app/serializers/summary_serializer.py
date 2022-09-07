from pathlib import Path
from statistics import mean
from typing import List

from rest_framework import serializers

from epic_app.exporters.summary_evolution_csv_exporter import SummaryEvolutionCsvFile
from epic_app.models.epic_answers import EvolutionAnswer, MultipleChoiceAnswer
from epic_app.models.epic_questions import (
    EvolutionChoiceType,
    EvolutionQuestion,
    LinkagesQuestion,
)
from epic_app.models.epic_user import EpicOrganization
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
    class Meta:
        model = Program
        fields = "__all__"

    def to_representation(self, instance: Program):
        organization_users = self.context["users"].all()
        user_ids = [eu.id for eu in organization_users]
        _query = EvolutionAnswer.objects.filter(
            user__in=user_ids, question__in=instance.questions
        ).all()

        def avg_answers(answers_list: List[EvolutionAnswer]) -> float:
            answers_as_int = map(EvolutionChoiceType.to_int, answers_list)
            return round(mean(answers_as_int), 2)

        _answers_summary = avg_answers(_query.values_list("selected_choice", flat=True))
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
            EvolutionQuestion.objects.all(),
            many=True,
            context={"request": self.context, "users": instance.organization_users},
        ).data

        return {
            "id": instance.pk,
            "organization": instance.name,
            "evolution_questions": _answers_summary,
        }


class SummaryEvolutionGraph:
    _summary_name = "evolution_summary.png"

    def __init__(self, evolution_summary: dict) -> None:
        self._evolution_summary = evolution_summary
        # Ideally we would have a class to have a better status, but at the moment
        # and due to budget reasons I rather not invest the time on it.
        self._is_valid = False
        self._error_message = ""

    def _execute_r_snippet(self, csv_file: Path) -> None:
        import rpy2.robjects as robjects

        robjects.r.source("/pathto/MyrScript.r", encoding="utf-8")

    def generate(self, graph_file: Path) -> Path:
        try:
            _csv_file = SummaryEvolutionCsvFile.from_serialized_data(self._evolution_summary).export(
                graph_file.parent
            )
            self._execute_r_snippet(_csv_file)
            self._is_valid = True
        except Exception as exc_info:
            self._is_valid = False
            self._error_message = str(exc_info)

    def is_valid(self) -> bool:
        return self._is_valid
