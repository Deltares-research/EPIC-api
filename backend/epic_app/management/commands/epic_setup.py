from pathlib import Path
from typing import Any, Optional

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from epic_app.importers import EpicAgencyImporter, EpicDomainImporter
from epic_app.models.epic_user import EpicUser


class Command(BaseCommand):
    help = "Sets the default EPIC database with a predefined admin user. If the database already exists then it removes it (and its migrations) and creates one from zero."
    # epic_setup.py -> commands -> management -> epic_app
    epic_app_dir: Path = Path(__file__).parent.parent.parent
    root_dir: Path = epic_app_dir.parent

    def _remove_migrations(self):
        """
        Removes all previous migrations.
        """
        migrations_dir = self.epic_app_dir / "migrations"
        for m_file in migrations_dir.glob("*.py"):
            if m_file.name != "__init__.py":
                self.stdout.write(
                    self.style.WARNING(f"Removing migration file: {m_file.name}")
                )
                m_file.unlink()

    def _cleanup_db(self):
        """
        Removes the current database.
        """
        db_path = self.root_dir / "db.sqlite3"
        if db_path.is_file():
            self.stdout.write(
                self.style.WARNING(f"Removing database file at {db_path}")
            )
            db_path.unlink()
        self._remove_migrations()
        self.stdout.write(
            self.style.SUCCESS("Successfully cleaned up previous database structure.")
        )

    def _import_files(self, test_data_dir: Path):
        """
        Imports all the available files to create a reliable test environment.

        Args:
            test_data_dir (Path): Path to the test directory.
        """
        epic_domain_csv = test_data_dir / "initial_epic_data.csv"
        if epic_domain_csv.is_file():
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    f"Importing main data from {epic_domain_csv}."
                )
            )
            EpicDomainImporter().import_csv(epic_domain_csv)
            self.stdout.write(self.style.SUCCESS("Import successful."))
        epic_agency_csv = test_data_dir / "agency_data.csv"
        if epic_agency_csv.is_file():
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    f"Importing agencies from {epic_agency_csv}."
                )
            )
            EpicAgencyImporter().import_csv(epic_agency_csv)
            self.stdout.write(self.style.SUCCESS("Import successful."))

    def _create_superuser(self):
        """
        Creates an admin 'superuser' with classic 'admin'/'admin' user/pass.
        """
        # Create an admin user.
        admin_user = User(
            username="admin",
            email="admin@testdb.com",
            first_name="Star",
            last_name="Lord",
        )
        admin_user.set_password("admin")
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        self.stdout.write(
            self.style.SUCCESS("Created superuser: 'admin', password: 'admin'.")
        )

    def _create_dummy_users(self):
        try:
            self._create_superuser()
        except:
            call_command("createsuperuser")

        # Create a few basic users.
        zelda = EpicUser.objects.create(username="Zelda", organization="Nintendo")
        zelda.set_password("zelda")
        ganon = EpicUser.objects.create(username="Ganon", organization="Nintendo")
        ganon.set_password("ganon")
        luke = EpicUser.objects.create(username="Luke", organization="Rebel Alliance")
        luke.set_password("luke")
        leia = EpicUser.objects.create(username="Leia", organization="Rebel Alliance")
        leia.set_password("leia")
        self.stdout.write(
            self.style.SUCCESS(
                "Created some 'dummy' users: 'Zelda', 'Ganon', 'Luke' and 'Leia'."
            )
        )

    def _import_test_db(self):
        test_data_dir: Path = self.epic_app_dir / "tests" / "test_data"
        if not test_data_dir.is_dir():
            self.stdout.write(
                self.style.ERROR(
                    f"No test data found at {test_data_dir}, database will be empty on start."
                )
            )
        try:
            self._import_files(test_data_dir)
            self._create_dummy_users()
        except Exception as e_info:
            call_command("flush")
            self.stdout.write(
                self.style.ERROR(
                    f"Could not correctly import test data, database will be empty on start. Detail error: {str(e_info)}."
                )
            )

    def _migrate_db(self):
        """
        Creates the current database structure as sqlite3 file.
        """
        call_command("makemigrations")
        call_command("migrate")
        self._import_test_db()

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        try:
            self._cleanup_db()
            self._migrate_db()
        except Exception as e_info:
            self.stdout.write(
                self.style.ERROR(f"Error setting up EPIC. Detailed info: {str(e_info)}")
            )