import pytest
import epic_app.models as epic_models
from django.contrib.auth.models import User

@pytest.fixture(autouse=True)
@pytest.mark.django_db
def default_test_db():
    # Areas
    alpha_area = epic_models.Area(name="alpha")
    alpha_area.save()
    beta_area = epic_models.Area(name="beta")
    beta_area.save()

    # Agency
    tia_agency = epic_models.Agency(name="T.I.A.")
    tia_agency.save()
    cia_agency = epic_models.Agency(name="C.I.A.")
    cia_agency.save()
    mi6_agency = epic_models.Agency(name="M.I.6")
    mi6_agency.save()
    rws_agency = epic_models.Agency(name="R.W.S.")
    rws_agency.save()

    # Groups
    first_group = epic_models.Group(name="first", area=alpha_area)
    first_group.save()
    second_group = epic_models.Group(name="second", area=alpha_area)
    second_group.save()
    third_group = epic_models.Group(name="third", area=beta_area)
    third_group.save()

    # Programs
    epic_models.Program(name="a", group=first_group, agency=tia_agency).save()
    epic_models.Program(name="b", group=first_group, agency=tia_agency).save()
    epic_models.Program(name="c", group=first_group, agency=cia_agency).save()
    epic_models.Program(name="d", group=second_group, agency=mi6_agency).save()
    epic_models.Program(name="e", group=third_group, agency=rws_agency).save()

@pytest.mark.django_db
class TestEpicUser:

    def test_init_epicuser(self):
        created_user = epic_models.EpicUser(organization='random')
        created_user.save()
        assert isinstance(created_user, epic_models.EpicUser)
        assert isinstance(created_user, User)
        assert created_user.is_superuser is False

@pytest.mark.django_db
class TestArea:
    def test_area_get_groups(self):
        alpha_area: epic_models.Area = epic_models.Area.objects.filter(name="alpha").first()
        assert isinstance(alpha_area, epic_models.Area)
        assert len(alpha_area.get_groups()) == 2
        group_names = [alpha_group.name for alpha_group in alpha_area.get_groups()]
        assert "first" in group_names
        assert "second" in group_names
        assert str(alpha_area) == "alpha"
    
    def test_delete_area_deletes_in_cascade(self):
        alpha_area: epic_models.Area = epic_models.Area.objects.filter(name="alpha").first()
        assert isinstance(alpha_area, epic_models.Area)
        
        # Delete model
        epic_models.Area.delete(alpha_area)

        # Verify cascade effect.
        assert not epic_models.Area.objects.filter(name="alpha").exists()
        # Groups deleted.
        assert not epic_models.Group.objects.filter(name="first").exists()
        assert not epic_models.Group.objects.filter(name="second").exists()
        # Programs deleted
        assert not epic_models.Program.objects.filter(name="a").exists()
        assert not epic_models.Program.objects.filter(name="b").exists()
        assert not epic_models.Program.objects.filter(name="c").exists()
        assert not epic_models.Program.objects.filter(name="d").exists()


@pytest.mark.django_db
class TestAgency:
    def test_agency_get_programs(self):
        tia_agency: epic_models.Agency = epic_models.Agency.objects.filter(name="T.I.A.").first()
        assert isinstance(tia_agency, epic_models.Agency)
        assert len(tia_agency.get_programs()) == 2
        program_names = [tia_program.name for tia_program in tia_agency.get_programs()]
        assert "a" in program_names
        assert "b" in program_names
        assert str(tia_agency) == "T.I.A."        

    def test_delete_agency_does_not_delete_in_cascade(self):
        tia_agency: epic_models.Agency = epic_models.Agency.objects.filter(name="T.I.A.").first()
        assert isinstance(tia_agency, epic_models.Agency)
        epic_models.Agency.delete(tia_agency)

        # Verify elements still exist
        program_names = ["a", "b"]
        for p_name in program_names:
            p_program: epic_models.Program = epic_models.Program.objects.filter(name=p_name).first()
            assert isinstance(p_program, epic_models.Program)
            assert p_program.agency is None    

@pytest.mark.django_db
class TestGroup:
    def test_group_get_programs(self):
        second_group: epic_models.Group = epic_models.Group.objects.filter(name="second").first()
        assert isinstance(second_group, epic_models.Group)
        assert isinstance(second_group.area, epic_models.Area)
        assert second_group.area.name == "alpha"
        assert len(second_group.get_programs()) == 1
        assert "d" == second_group.get_programs()[0].name
        assert str(second_group) == "second"  
    
    def test_delete_group_deletes_in_cascade(self):
        second_group: epic_models.Group = epic_models.Group.objects.filter(name="second").first()
        area = second_group.area
        assert isinstance(second_group, epic_models.Group)
        
        # Delete element
        epic_models.Group.delete(second_group)

        # Verify elements still exist
        assert not epic_models.Program.objects.filter(name="d").exists()
        assert epic_models.Area.objects.filter(name=area.name).exists()

@pytest.mark.django_db
class TestProgram:
    def test_program_data(self):
        program: epic_models.Program = epic_models.Program.objects.filter(name="e").first()
        assert isinstance(program, epic_models.Program)
        assert isinstance(program.agency, epic_models.Agency)
        assert program.agency.name == "R.W.S."
        assert isinstance(program.group, epic_models.Group)
        assert program.group.name == "third"
    
    def test_program_delete_does_not_delete_in_cascade(self):
        program: epic_models.Program = epic_models.Program.objects.filter(name="e").first()
        g_name: str = program.group.name
        a_name: str = program.agency.name
        assert isinstance(program, epic_models.Program)
        epic_models.Program.delete(program)
        assert not epic_models.Program.objects.filter(name="e").exists()
        assert epic_models.Agency.objects.filter(name=a_name).exists()
        assert epic_models.Group.objects.filter(name=g_name).exists()

@pytest.mark.django_db
class TestAnswer:
    pass