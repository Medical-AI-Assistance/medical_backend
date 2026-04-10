from rest_framework import serializers
from healthassessment.models import Section, Question, Option, Answer


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class OptionSerializer(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(
        slug_field="reference_id", 
        queryset=Question.objects.all()
    )

    class Meta:
        model = Option
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    section = serializers.SlugRelatedField(
        slug_field="reference_id", 
        queryset=Section.objects.all()
    )

    class Meta:
        model = Question
        fields = "__all__"


class AnswerSerializer(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(
        slug_field="reference_id",
        read_only=True
    )
    
    class Meta:
        model = Answer
        fields = "__all__"
        read_only_fields = ["user"]