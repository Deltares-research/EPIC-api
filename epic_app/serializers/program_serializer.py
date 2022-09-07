from rest_framework import serializers

from epic_app.models.models import Program, ProgramReference


class ProgramReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramReference
        fields = ("description", "link")


class ProgramSerializer(serializers.ModelSerializer):
    """
    Serializer for 'Program'
    """

    references = ProgramReferenceSerializer(many=True)

    class Meta:
        """
        Overriden meta class for serializing purposes.
        """

        model = Program
        fields = (
            "url",
            "id",
            "name",
            "description",
            "references",
            "agencies",
            "group",
            "questions",
        )


class SimpleProgramSerializer(serializers.ModelSerializer):
    """
    Serializer for 'Program' without embedded questions.
    """

    references = ProgramReferenceSerializer(many=True)

    class Meta:
        """
        Overriden meta class for serializing purposes.
        """

        model = Program
        fields = ("url", "id", "name", "description", "references")
