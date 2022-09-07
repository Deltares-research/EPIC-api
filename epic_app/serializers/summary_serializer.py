from pathlib import Path
from statistics import mean
from typing import Any, List

from rest_framework import serializers

from epic_app.exporters.summary_evolution_csv_exporter import SummaryEvolutionCsvFile
from epic_app.externals import eram_visuals
from epic_app.models.epic_answers import EvolutionAnswer, MultipleChoiceAnswer
from epic_app.models.epic_questions import (
    EvolutionChoiceType,
    EvolutionQuestion,
    LinkagesQuestion,
)
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

    def _get_user_average_evolution_program(
        self, org_user: EpicUser, program: Program
    ) -> float:
        _answers = (
            EvolutionAnswer.objects.filter(
                user=org_user, question__in=program.questions.all()
            )
            .all()
            .values_list("selected_choice", flat=True)
        )
        answers_as_int = list(map(EvolutionChoiceType.to_int, _answers))
        if not answers_as_int:
            return 0
        return mean(answers_as_int)

    def _get_organization_average_evolution_program(
        self, epic_org: EpicOrganization, program: Program
    ) -> float:
        avg_list = []
        _users = epic_org.organization_users.all()
        if not _users:
            return 0
        for epic_user in _users:
            avg_list.append(
                self._get_user_average_evolution_program(epic_user, program)
            )
        return mean(avg_list)

    def to_representation(self, instance: Program):
        _organizations = self.context["organizations"].all()
        _org_averages = [
            self._get_organization_average_evolution_program(epic_org, instance)
            for epic_org in list(_organizations)
        ]
        _answers_summary = round(mean(_org_averages), 2)
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


class SummaryEvolutionGraph:
    _summary_name = "evolution_summary.png"

    def __init__(self, evolution_summary: dict) -> None:
        self._evolution_summary = evolution_summary
        # Ideally we would have a class to have a better status, but at the moment
        # and due to budget reasons I rather not invest the time on it.
        self._is_valid = False
        self._error_message = ""

    @staticmethod
    def execute_r_snippet(evo_csv_file: Path, evo_png_file: Path) -> None:
        # Method based on the README.md from the repository:
        # https://github.com/tanerumit/ERAMVisuals/
        import rpy2.robjects as robjects
        import rpy2.robjects.packages as rpackages

        def install_required_packages(packages: List[str]):
            utils = rpackages.importr("utils")
            # select a mirror for R packages
            utils.chooseCRANmirror(ind=1)  # select the first mirror in the list

            # R vector of strings
            from rpy2.robjects.vectors import StrVector

            # Selectively install what needs to be install.
            # We are fancy, just because we can.
            names_to_install = [x for x in packages if not rpackages.isinstalled(x)]
            if len(names_to_install) > 0:
                utils.install_packages(StrVector(names_to_install))

        def radial_plot_func() -> Any:
            r_source = robjects.r["source"]
            script_path = eram_visuals / "ERAMRadialPlot.R"
            r_source(str(script_path))
            return r_source

        _required_packages = ("scales", "ggplot2", "dplyr", "readr", "stringr")
        install_required_packages(_required_packages)
        _radial_plot = radial_plot_func()
        _readr = rpackages.importr("readr")
        _ggplot2 = rpackages.importr("ggplot2")
        _data = _readr.read_csv(str(evo_csv_file))
        _radial_data = robjects.r["ERAMRadialPlot"](_data)

        # Save png and pdf.
        _ggplot2.ggsave(
            filename=str(evo_png_file), plot=_radial_data, width=8, height=8
        )
        _ggplot2.ggsave(
            filename=str(evo_png_file.with_suffix(".pdf")),
            plot=_radial_data,
            width=8,
            height=8,
        )

    def generate(self, output_dir: Path) -> Path:
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)
        _graph_path = output_dir / self._summary_name
        try:
            _csv_file = SummaryEvolutionCsvFile.from_serialized_data(
                self._evolution_summary
            ).export(output_dir)
            self.execute_r_snippet(_csv_file, _graph_path)
            self._is_valid = True
        except Exception as exc_info:
            self._is_valid = False
            self._error_message = str(exc_info)
        finally:
            return _graph_path

    def is_valid(self) -> bool:
        return self._is_valid
