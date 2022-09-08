from pathlib import Path
from typing import List, Optional

import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages

from epic_app.externals import eram_visuals_script
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
        r_source = robjects.r["source"]
        script_path = eram_visuals_script
        r_source(str(script_path))

    def _run_script(self) -> None:
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

    def initialize(self) -> None:
        self._status.to_initialized()
        _output_dir = self._output_file.parent
        if not _output_dir.exists():
            _output_dir.mkdir(parents=True)
        if self._output_file.is_file():
            self._output_file.rename(self._get_backup_output_file())

    def finalize(self) -> None:
        self._status.to_succeeded()

    def finalize_with_error(self, error_mssg: str) -> None:
        # Execution failed
        self._status.to_failed(error_mssg)
        _old_file = self._get_backup_output_file()
        if _old_file and _old_file.exists():
            _old_file.rename(self._output_file)

    def execute(self) -> None:
        try:
            self.initialize()
            self._run_script()
            self.finalize()
        except Exception as e_info:
            self.finalize_with_error(str(e_info))
