import itertools

from rest_framework import serializers

from epic_app.models.epic_answers import MultipleChoiceAnswer
from epic_app.models.epic_questions import LinkagesQuestion


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
