from rest_framework import serializers
from healthassessment.models import Section, Question, Option, Answer, AssessmentType

class AssessmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentType
        fields = ["reference_id", "name", "description"]

class SectionSerializer(serializers.ModelSerializer):
    assessment_type = serializers.SlugRelatedField(
        slug_field="reference_id",
        queryset=AssessmentType.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Section
        fields = ["reference_id", "name", "assessment_type"]


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


# --- Bulk create: assessment type + sections + questions + options in one request ---

class QuestionWithOptionsSerializer(serializers.Serializer):
    question_id = serializers.UUIDField(required=False)
    question_text = serializers.CharField()
    input_type = serializers.ChoiceField(choices=["text", "number", "mcq"])
    options = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )

    def validate(self, data):
        if data["input_type"] == "mcq" and not data.get("options"):
            raise serializers.ValidationError(
                {"options": "Options are required for MCQ questions."}
            )
        if data["input_type"] in ("text", "number") and data.get("options"):
            raise serializers.ValidationError(
                {"options": f"Options are not allowed for '{data['input_type']}' questions."}
            )
        return data


class SectionWithQuestionsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    assessment_type = serializers.SlugRelatedField(
        slug_field="reference_id",
        queryset=AssessmentType.objects.all(),
        required=False,
        allow_null=True
    )
    questions = QuestionWithOptionsSerializer(many=True, required=False, default=list)

    def validate(self, data):
        assessment_type = data.get("assessment_type")
        name = data.get("name")
        if Section.objects.filter(assessment_type=assessment_type, name=name).exists():
            raise serializers.ValidationError(
                {"name": f"A section named '{name}' already exists under this assessment type."}
            )

        # Check for duplicate question texts within this section request
        question_texts = [q["question_text"] for q in data.get("questions", [])]
        duplicates = {t for t in question_texts if question_texts.count(t) > 1}
        if duplicates:
            raise serializers.ValidationError(
                {"questions": f"Duplicate question(s) in request: {', '.join(duplicates)}"}
            )
        return data

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        section = Section.objects.create(**validated_data)

        for q_data in questions_data:
            options_texts = q_data.pop("options", [])
            question = Question.objects.create(
                section=section,
                assessment_type=section.assessment_type,
                **q_data
            )
            for opt_text in options_texts:
                Option.objects.create(question=question, option_text=opt_text)

        return section


class SectionWithQuestionsUpdateSerializer(serializers.Serializer):
    section_id = serializers.UUIDField()
    name = serializers.CharField(max_length=200)
    assessment_type = serializers.SlugRelatedField(
        slug_field="reference_id",
        queryset=AssessmentType.objects.all(),
        required=False,
        allow_null=True
    )
    
    questions = QuestionWithOptionsSerializer(many=True, required=False)


    def validate(self, data):
        section_id = data.get("section_id")
        questions = data.get("questions", [])

        try:
            section = Section.objects.get(reference_id=section_id)
        except Section.DoesNotExist:
            raise serializers.ValidationError({
                "message": "Section not found."
            })

        existing_questions = section.question_set.all()
        existing_ids = set(str(q.reference_id) for q in existing_questions)

        invalid_count = 0

        for q in questions:
            q_id = q.get("question_id")
            if q_id and str(q_id) not in existing_ids:
                invalid_count += 1

        if invalid_count > 0:
            raise serializers.ValidationError({
                "message": f"{invalid_count} question(s) do not exist in this section."
            })

        return data

    def update(self, instance, validated_data):
        questions_data = validated_data.pop("questions", [])

        # 🔹 Update section
        instance.name = validated_data.get("name", instance.name)
        instance.assessment_type = validated_data.get("assessment_type", instance.assessment_type)
        instance.save()

        existing_questions = {str(q.reference_id): q for q in instance.question_set.all()}
        incoming_ids = []

        # 🔹 Process questions
        for q_data in questions_data:
            q_id = str(q_data.get("question_id", ""))

            # if q_id:
            #     q_id = str(q_id)

            #     if q_id not in existing_questions:
            #         raise serializers.ValidationError({
            #             "questions": f"Question with id {q_id} does not exist in this section."
            #     })

            if q_id and q_id in existing_questions:
                # UPDATE
                question = existing_questions[q_id]
                question.question_text = q_data.get("question_text", question.question_text)
                question.input_type = q_data.get("input_type", question.input_type)
                question.save()

                incoming_ids.append(q_id)

                # 🔸 Handle options
                if question.input_type == "mcq":
                    options = q_data.get("options", [])
                    question.options.all().delete()
                    for opt in options:
                        Option.objects.create(question=question, option_text=opt)

            else:
                # CREATE
                options = q_data.pop("options", [])
                question = Question.objects.create(
                    section=instance,
                    assessment_type=instance.assessment_type,
                    **q_data
                )

                for opt in options:
                    Option.objects.create(question=question, option_text=opt)

        # 🔹 DELETE removed questions
        for q_id, q_obj in existing_questions.items():
            if q_id not in incoming_ids:
                q_obj.delete()

        return instance

class SectionBulkSerializer(serializers.Serializer):
    """One section entry inside AssessmentTypeWithSectionsSerializer."""
    name = serializers.CharField(max_length=200)
    questions = QuestionWithOptionsSerializer(many=True, required=False, default=list)


class AssessmentTypeWithSectionsSerializer(serializers.Serializer):
    """
    Bulk-create an assessment type with all its sections, questions, and options
    in a single request.
    """
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    sections = SectionBulkSerializer(many=True, required=False, default=list)

    def validate_name(self, value):
        if AssessmentType.objects.filter(name=value).exists():
            raise serializers.ValidationError("An assessment type with this name already exists.")
        return value

    def validate(self, data):
        sections = data.get("sections", [])
        section_names = [s["name"] for s in sections]

        # Duplicate section names within the request
        duplicates = {n for n in section_names if section_names.count(n) > 1}
        if duplicates:
            raise serializers.ValidationError(
                {"sections": f"Duplicate section name(s) in request: {', '.join(duplicates)}"}
            )

        # Duplicate question texts within each section in the request
        for section in sections:
            question_texts = [q["question_text"] for q in section.get("questions", [])]
            dup_questions = {t for t in question_texts if question_texts.count(t) > 1}
            if dup_questions:
                raise serializers.ValidationError(
                    {
                        "sections": (
                            f"Section '{section['name']}' has duplicate question(s): "
                            f"{', '.join(dup_questions)}"
                        )
                    }
                )

        return data

    def create(self, validated_data):
        sections_data = validated_data.pop("sections", [])
        assessment_type = AssessmentType.objects.create(**validated_data)

        for section_data in sections_data:
            questions_data = section_data.pop("questions", [])
            section = Section.objects.create(assessment_type=assessment_type, **section_data)

            for q_data in questions_data:
                options_texts = q_data.pop("options", [])
                question = Question.objects.create(
                    section=section,
                    assessment_type=assessment_type,
                    **q_data
                )
                for opt_text in options_texts:
                    Option.objects.create(question=question, option_text=opt_text)

        return assessment_type