# Create your views here.
from rest_framework import viewsets, permissions

from epic_app.serializers import EpicUserSerializer, QuestionSerializer, AnswerSerializer, AreaSerializer, GroupSerializer, ProgramSerializer
from epic_app.models import EpicUser, Question, Answer, Area, Group, Program

class EpicUserViewSet(viewsets.ModelViewSet):
    """
    Default view set for 'EpicUser'

    Args:
        viewsets (ModelViewSet): Derives directly from ModelViewSet
    """
    queryset = EpicUser.objects.all().order_by('username')
    serializer_class = EpicUserSerializer
    permission_classes = [permissions.DjangoModelPermissions]

class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Default view set for 'Area'

    Args:
        viewsets (ModelViewSet): Derives directly from ModelViewSet
    """
    queryset = Area.objects.all().order_by('name')
    serializer_class = AreaSerializer
    permission_classes = [permissions.DjangoModelPermissions]

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Default view set for 'Group'

    Args:
        viewsets (ModelViewSet): Derives directly from ModelViewSet
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.DjangoModelPermissions]

class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Default view set for 'Program'

    Args:
        viewsets (ModelViewSet): Derives directly from ModelViewSet
    """
    queryset = Program.objects.all().order_by('name')
    serializer_class = ProgramSerializer
    permission_classes = [permissions.DjangoModelPermissions]

class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Default view set for 'Question'

    Args:
        viewsets (ModelViewSet): Derives directly from ModelViewSet
    """
    queryset = Question.objects.all().order_by('description')
    serializer_class = QuestionSerializer
    permission_classes = [permissions.DjangoModelPermissions]

class AnswerViewSet(viewsets.ModelViewSet):
    """
    Default view set for 'Answer'

    Args:
        viewsets (ModelViewSet): Derives directly from ModelViewSet
    """
    queryset = Answer.objects.all().order_by('user')
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]