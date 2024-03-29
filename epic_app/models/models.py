from __future__ import annotations

from typing import List, Optional

from django.db import models
from django.forms import ValidationError


# region Default models
class Area(models.Model):
    """
    Higher up entity containing a set of Groups.

    Args:
        models (models.Model): Derives directly from the base class Model.
    """

    name: str = models.CharField(max_length=250)

    def get_groups(self) -> List[Group]:
        """
        Gets a list of groups whose area is the caller.

        Returns:
            List[Group]: List of groups frot this area.
        """
        return Group.objects.filter(area=self).all()

    def __str__(self) -> str:
        return self.name


class Agency(models.Model):

    name: str = models.CharField(max_length=250)

    class Meta:
        verbose_name_plural = "Agencies"

    def get_programs(self) -> List[Program]:
        """
        Gets all the programs that belong to this agency.

        Returns:
            List[Program]: List of programs registered for this agency.
        """
        return Program.objects.filter(agencies=self).all()

    def __str__(self) -> str:
        return self.name


class Group(models.Model):
    """
    Higher up entity containing one or programs.

    Args:
        models (models.Model): Derives directly from the base class Model.
    """

    name: str = models.CharField(max_length=250)
    area: Area = models.ForeignKey(
        to=Area, on_delete=models.CASCADE, related_name="groups"
    )

    def get_programs(self) -> List[Program]:
        """
        Gets a list of programs whose groups is the caller.

        Returns:
            List[Program]: List of programs for this group.
        """
        return Program.objects.filter(group=self).all()

    def __str__(self) -> str:
        return self.name


class Program(models.Model):
    """
    Higher up entity containing one or many questions and answers.

    Args:
        models (models.Model): Derives directly from the base class Model.
    """

    name: str = models.CharField(
        max_length=250,
        unique=True,
    )
    description: str = models.TextField(
        blank=False,
        null=False,
    )
    agencies: List[Agency] = models.ManyToManyField(
        to=Agency, blank=True, related_name="programs"
    )
    group: Group = models.ForeignKey(
        to=Group, on_delete=models.CASCADE, related_name="programs"
    )

    @staticmethod
    def check_unique_name(value: str):
        """
        Checks whether there is a Program with provided value as a name.

        Args:
            value (str): Name to give to a new Program.

        Raises:
            ValidationError: When there is already a Program with the same case insensitive name.
        """
        existing_program = Program.get_program_by_name(value)
        if existing_program:
            raise ValidationError(
                f"There's already a Program with the name: {existing_program.name}."
            )

    @staticmethod
    def get_program_by_name(value: str) -> Optional[Program]:
        """
        Gets the existing program wich name (case insensitive) matches the given value.

        Args:
            value (str): Program name.

        Returns:
            Optional[Program]: Found program.
        """
        return next(
            (p for p in Program.objects.all() if p.name.lower() == value.lower()), None
        )

    def save(self, *args, **kwargs) -> None:
        self.check_unique_name(self.name)
        return super(Program, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class ProgramReference(models.Model):
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True)
    program: Program = models.ForeignKey(
        to=Program, on_delete=models.CASCADE, related_name="references"
    )

    def __str__(self) -> str:
        return f"{self.program.pk}: {self.link} - {self.description}"


# endregion
