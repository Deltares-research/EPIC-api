from pathlib import Path
from typing import List, final

from epic_app.externals.ERAMVisuals import eram_visuals_script
from epic_app.externals.external_wrapper_base import (
    ExternalWrapperBase,
    ExternalWrapperStatus,
)


class EramVisualsWrapper(ExternalWrapperBase):

    _required_packages = ("scales", "ggplot2", "dplyr", "readr", "stringr")
    _status: ExternalWrapperStatus = None

    def __init__(self, input_file: Path, output_file: Path) -> None:
        super().__init__()
        self._status = ExternalWrapperStatus()
        self._input_file = input_file
        self._output_file = output_file

    @property
    def status(self) -> ExternalWrapperStatus:
        return self._status

    def _install_required_packages(self, packages: List[str]) -> None:
        import rpy2.robjects.packages as rpackages

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

    def _set_radial_plot_func(self) -> None:
        import rpy2.robjects as robjects

        r_source = robjects.r["source"]
        script_path = eram_visuals_script
        r_source(str(script_path))

    def _run_script(self) -> None:
        import rpy2.robjects as robjects
        import rpy2.robjects.packages as rpackages

        # Method based on the README.md from the repository:
        # https://github.com/tanerumit/ERAMVisuals/
        self._install_required_packages(self._required_packages)
        self._set_radial_plot_func()
        _readr = rpackages.importr("readr")
        _ggplot2 = rpackages.importr("ggplot2")
        _data = _readr.read_csv(str(self._input_file))
        _radial_data = robjects.r["ERAMRadialPlot"](_data)

        # Save png and pdf.
        _ggplot2.ggsave(
            filename=str(self._output_file), plot=_radial_data, width=8, height=8
        )
        _ggplot2.ggsave(
            filename=str(self._output_file.with_suffix(".pdf")),
            plot=_radial_data,
            width=8,
            height=8,
        )

    def _get_backup_output_file(self) -> Path:
        return self._output_file.parent / (self._output_file.name + ".old")

    def _get_pdf_output_file(self) -> Path:
        return self._output_file.with_suffix(".pdf")

    def _get_backup_pdf_output_file(self) -> Path:
        _pdf_file = self._get_pdf_output_file().name
        return self._output_file.parent / (_pdf_file + ".old")

    def initialize(self) -> None:
        self._status.to_initialized()
        _output_dir = self._output_file.parent
        if not _output_dir.exists():
            _output_dir.mkdir(parents=True)

        def initialize_backup(from_file: Path, to_file: Path) -> None:
            if to_file.exists():
                to_file.unlink()
            if from_file.is_file():
                from_file.rename(to_file)

        initialize_backup(self._output_file, self._get_backup_output_file())
        initialize_backup(
            self._get_pdf_output_file(), self._get_backup_pdf_output_file()
        )

    def _finalize_backup_file(self, failed: bool) -> None:
        def apply_backup(from_file: Path, to_file: Path) -> None:
            if failed:
                # Then we need to bring back the backup as a file.
                if to_file.exists():
                    # Remove the 'possibly' generated new file.
                    to_file.unlink()
                # Rename the backup to be the source file.
                from_file.rename(to_file)
            # Remove the backup file and leave only the 'real one'.
            if from_file.exists():
                from_file.unlink()

        apply_backup(self._get_backup_output_file(), self._output_file)
        apply_backup(self._get_backup_pdf_output_file(), self._get_pdf_output_file())

    def finalize(self) -> None:
        self._status.to_succeeded()
        self._finalize_backup_file(failed=False)

    def finalize_with_error(self, error_mssg: str) -> None:
        # Execution failed
        self._status.to_failed(error_mssg)
        self._finalize_backup_file(failed=True)

    def execute(self) -> None:
        try:
            self.initialize()
            self._run_script()
            self.finalize()
        except Exception as e_info:
            self.finalize_with_error(str(e_info))
