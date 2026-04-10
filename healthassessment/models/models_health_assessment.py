from django.db import models
from generic.models import GenericEntity, GenericIdEntity
from django.conf import settings


class Section(GenericIdEntity):
    name = models.CharField(max_length=200)

    class Meta:
        db_table = "healthassessment_section"
        managed = True

    def __str__(self):
        return self.name


class Question(GenericIdEntity):
    INPUT_TYPES = [
        ("text", "Text"),
        ("number", "Number"),
        ("mcq", "Multiple Choice"),
    ]

    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    question_text = models.TextField()
    input_type = models.CharField(max_length=20, choices=INPUT_TYPES)

    class Meta:
        db_table = "healthassessment_question"
        managed = True

    def __str__(self):
        return self.question_text


class Option(GenericIdEntity):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    option_text = models.CharField(max_length=200)

    class Meta:
        db_table = "healthassessment_option"
        managed = True

    def __str__(self):
        return self.option_text
    

class Answer(GenericIdEntity):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()

    class Meta:
        db_table = "healthassessment_answer"
        managed = True