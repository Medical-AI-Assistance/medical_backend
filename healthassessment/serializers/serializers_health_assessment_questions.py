from rest_framework import serializers
from healthassessment.models import Section, Question, Option, Answer


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["reference_id", "name"]


class OptionSerializer(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(
        slug_field="reference_id", 
        queryset=Question.objects.all()
    )

    class Meta:
        model = Option
        fields = ["reference_id", "question", "option_text"]


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    section = serializers.SlugRelatedField(
        slug_field="reference_id", 
        queryset=Section.objects.all()
    )

    class Meta:
        model = Question
        fields = ["reference_id", "section", "options", "question_text", "input_type"]


class AnswerSerializer(serializers.ModelSerializer):
    question = serializers.SlugRelatedField(
        slug_field="reference_id",
        read_only=True
    )
    
    class Meta:
        model = Answer
        fields = ["reference_id", "user", "session", "question", "answer_text"]
        read_only_fields = ["user", "session"]  