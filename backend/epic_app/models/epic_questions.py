from __future__ import annotations

import abc

from django.db import IntegrityError, models

from epic_app.models import models as base_models


class Question(models.Model):

    title: str = models.CharField(null=False, blank=False, max_length=150)
    program: base_models.Program = models.ForeignKey(
        to=base_models.Program, on_delete=models.CASCADE, related_name="questions"
    )

    class Meta:
        unique_together = ["title", "program"]

    def __str__(self) -> str:
        return self.title[0:15]

    @abc.abstractmethod
    def get_answer(self):
        raise NotImplementedError


class NationalFrameworkQuestion(Question):
    """
    Question of type Yes / No and Justify.
    """

    description: str = models.TextField(null=False, blank=False)


class EvolutionChoiceType(models.TextChoices):
    NASCENT = "Nascent"
    ENGAGED = "Engaged"
    CAPABLE = "Capable"
    EFFECTIVE = "Effective"


class EvolutionQuestion(Question):
    """
    Question of type 'pick one' between four categories and Justify.
    """

    # Single choice among four options
    nascent_description: str = models.TextField(
        null=False, blank=False, verbose_name=str(EvolutionChoiceType.NASCENT)
    )
    engaged_description: str = models.TextField(
        null=False, blank=False, verbose_name=str(EvolutionChoiceType.ENGAGED)
    )
    capable_description: str = models.TextField(
        null=False, blank=False, verbose_name=str(EvolutionChoiceType.CAPABLE)
    )
    effective_description: str = models.TextField(
        null=False, blank=False, verbose_name=str(EvolutionChoiceType.EFFECTIVE)
    )


class LinkagesQuestion(Question):
    """
    Question of multiple (max 3) choices between all programs registered in the database.
    """

    def save(self, *args, **kwargs) -> None:
        """
        Overriding the default save method to inject a 'fake' OneToOne constraint on the 'program' field.

        Raises:
            IntegrityError: When there's already a LinkagesQuestion for the same program.
        """
        # In theory this could be done with the OneToOne relationship. However I'm unable to override that field or the Meta class.
        if LinkagesQuestion.objects.filter(program=self.program).exists():
            raise IntegrityError(
                "UNIQUE constraint failed: epic_app_question.program_id"
            )
        return super().save(*args, **kwargs)


# region Cross-Reference Tables
class Answer(models.Model):
    """
    Cross reference table to define the bounding relationship between a User and the answers they give to each question.

    Args:
        models (models.Model): Derives directly from base class Model.
    """

    user = models.ForeignKey(
        to=base_models.EpicUser, on_delete=models.CASCADE, related_name="user_answers"
    )
    question = models.ForeignKey(
        to=Question, on_delete=models.CASCADE, related_name="question_answers"
    )

    class Meta:
        unique_together = ["user", "question"]

    def __str__(self) -> str:
        return f"[{self.user}] {self.question}"


class YesNoAnswer(Answer):
    class YesNoAnswerType(models.TextChoices):
        """
        Defines the Yes / No answer types.

        Args:
            models (models.TextChocies): Derives directly from the base class TextChoices.
        """

        YES = "Y"
        NO = "N"

    short_answer: str = models.CharField(
        YesNoAnswerType.choices, max_length=50, blank=False
    )
    justify_answer: str = models.TextField(blank=False)


class SingleChoiceAnswer(Answer):
    selected_choice: str = models.CharField(
        EvolutionChoiceType.choices, max_length=50, blank=False
    )
    justify_answer: str = models.TextField(blank=False)

    def get_selected_choice_text(self) -> str:
        return next(
            c_field
            for c_field in self._meta.get_fields()
            if c_field.verbose_name.lower() == self.selected_choice.lower()
        )


class MultipleChoiceAnswer(Answer):
    selected_programs = models.ManyToManyRel(
        to=base_models.Program, blank=False, related_name="selected_answers"
    )


# endregion
