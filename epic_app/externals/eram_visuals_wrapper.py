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

    def __init__(self) -> None:
        super().__init__()
        self._status = ExternalWrapperStatus()

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

    def _run_script(self, csv_input_file: Path, png_output_file: Path) -> None:
        self._install_required_packages(self._required_packages)
        self._set_radial_plot_func()
        _readr = rpackages.importr("readr")
        _ggplot2 = rpackages.importr("ggplot2")
        _data = _readr.read_csv(str(csv_input_file))
        _radial_data = robjects.r["ERAMRadialPlot"](_data)

        # Save png and pdf.
        _ggplot2.ggsave(
            filename=str(png_output_file), plot=_radial_data, width=8, height=8
        )
        _ggplot2.ggsave(
            filename=str(png_output_file.with_suffix(".pdf")),
            plot=_radial_data,
            width=8,
            height=8,
        )

    def execute(self, configuration_attrs: dict) -> None:
        # Method based on the README.md from the repository:
        # https://github.com/tanerumit/ERAMVisuals/
        self._status.to_initialized()
        _csv_input_file = configuration_attrs.get("input_file", None)
        _png_output_file = configuration_attrs.get("output_file", None)
        _old_file: Optional[Path] = None
        try:
            if not _png_output_file.parent.exists():
                _png_output_file.parent.mkdir(parents=True)
            if _png_output_file.is_file():
                _old_file = _png_output_file.rename(f"{_png_output_file}.old")
            self._run_script(_csv_input_file, _png_output_file)
            self._status.to_succeeded()
        except Exception as e_info:
            self._status.to_failed(str(e_info))
            # Recover the previous .png in case the execution failed.
            if _old_file and _old_file.is_file():
                _old_file.rename(_old_file.with_suffix(""))
