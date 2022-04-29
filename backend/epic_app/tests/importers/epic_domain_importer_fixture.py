from typing import Type

import pytest

from epic_app.importers.xlsx import EpicDomainImporter
from epic_app.importers.xlsx.base_importer import BaseEpicImporter
from epic_app.management.commands import epic_setup
from epic_app.tests import test_data_dir


@pytest.fixture(autouse=False)
def default_epic_domain_data():
    """
    Fixture to load the predefined database so we can test importing agencies correctly.
    """
    # Define test data
    test_file = test_data_dir / "xlsx" / "initial_epic_data.xlsx"
    assert test_file.is_file()
    EpicDomainImporter().import_file(test_file)


@pytest.fixture(autouse=False)
def full_epic_domain_data():
    epic_setup.Command().handle()
