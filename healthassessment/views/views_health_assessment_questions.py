from uritemplate import partial
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from healthassessment.models import Section, Question, Option, Answer, AssessmentType
from healthassessment.serializers import (
    SectionSerializer,
    QuestionSerializer,
    OptionSerializer,
    AnswerSerializer,
    AssessmentTypeSerializer,
    SectionWithQuestionsSerializer,
    AssessmentTypeWithSectionsSerializer,
    SectionWithQuestionsUpdateSerializer,
    AssessmentTypeFullTreeSerializer,
)
from core import permissions
from core.authentication import CookieJWTAuthentication 


class AssessmentTypeListAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        assessment_types = AssessmentType.objects.all()
        serializer = AssessmentTypeSerializer(assessment_types, many=True)
        return Response({
            "message": "Assessment types fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
class AssessmentTypeCreateAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AssessmentTypeSerializer(data=request.data)

        if not request.data.get("name"):
            return Response({
                "message": "Name is required",
            }, status=status.HTTP_400_BAD_REQUEST)

        assessment_type = AssessmentType.objects.filter(name=request.data.get("name")).first()
        if assessment_type:
            return Response({
                "message": "Assessment type already exists",
            }, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Assessment type created successfully",
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Assessment type creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class AssessmentTypeDetailAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference_id):
        try:
            assessment_type = AssessmentType.objects.get(reference_id=reference_id)
        except AssessmentType.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = AssessmentTypeSerializer(assessment_type)
        return Response({
            "message": "Assessment type fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

class AssessmentTypeUpdateAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, reference_id):
        try:
            assessment_type = AssessmentType.objects.get(reference_id=reference_id)
        except AssessmentType.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = AssessmentTypeSerializer(assessment_type, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Assessment type updated successfully",
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Assessment type update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class AssessmentTypeDeleteAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, reference_id):
        try:
            assessment_type = AssessmentType.objects.get(reference_id=reference_id)
        except AssessmentType.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        assessment_type.delete()
        return Response({"message": "Deleted"}, status=status.HTTP_200_OK)
    
    

class SectionListAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sections = Section.objects.filter(is_draft=False)
        serializer = SectionSerializer(sections, many=True)
        return Response({
            "message": "Sections fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class AssessmentTypeSectionsAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference_id):
        try:
            assessment_type = AssessmentType.objects.get(reference_id=reference_id)
        except AssessmentType.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        sections = Section.objects.filter(assessment_type=assessment_type, is_draft=False)
        serializer = SectionSerializer(sections, many=True)
        return Response({
            "message": "Sections fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class SectionCreateAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SectionSerializer(data=request.data)

        section = Section.objects.filter(name=request.data.get("name")).first()
        if section:
            return Response({
                "message": "Section already exists",
            }, status=status.HTTP_400_BAD_REQUEST)  

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Section created successfully",
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Section creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class SectionDetailAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference_id):
        try:
            section = Section.objects.get(reference_id=reference_id)
        except Section.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = SectionSerializer(section)
        return Response(serializer.data)
    

class SectionUpdateAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, reference_id):
        try:
            section = Section.objects.get(reference_id=reference_id)
        except Section.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = SectionSerializer(section, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Section updated successfully",
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Section update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class SectionDeleteAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, reference_id):
        try:
            section = Section.objects.get(reference_id=reference_id)
        except Section.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        section.delete()
        return Response({"message": "Deleted"})


class SectionQuestionsDeleteAPIView(APIView):
    """
    DELETE /health/sections/<reference_id>/questions/delete/

    Deletes ALL questions (and their options via CASCADE) that belong
    to the given section. Does NOT delete the section itself.

    Why filter by section only (not assessment_type)?
    The Question.assessment_type FK is denormalised data — it always
    mirrors the section's own assessment_type. Filtering by section is
    the canonical, authoritative relationship.
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, reference_id):
        try:
            section = Section.objects.get(reference_id=reference_id)
            section_id = section.reference_id
            section_name = section.name

        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=status.HTTP_404_NOT_FOUND)
        
        question_count = Question.objects.filter(section=section).count()

        deleted_count, _ = Question.objects.filter(section=section).delete()
        section.delete()

        return Response({
            "message": f"All questions for section '{section_name}' deleted successfully",
            "section_id": str(section_id),
            "section_name": section_name,
            "questions_deleted": question_count,
        }, status=status.HTTP_200_OK)


class QuestionListAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        sections = Section.objects.filter(is_draft=False)

        data = []

        for section in sections:

            questions_data = []

            questions = Question.objects.filter(section=section)

            for q in questions:

                options = []

                if q.input_type == "mcq":
                    options = [
                        {"reference_id": opt.reference_id, "text": opt.option_text}
                        for opt in q.options.all()
                    ]

                questions_data.append({
                    "reference_id": q.reference_id,
                    "question": q.question_text,
                    "type": q.input_type,
                    "options": options
                })

            data.append({
                "section": section.name,
                "questions": questions_data
            })

        return Response(data)
    

class QuestionCreateAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)

 
        if not request.data.get("section"):
            return Response({
                "message": "Section is required",
            }, status=status.HTTP_400_BAD_REQUEST)

        if not request.data.get("question_text"):
            return Response({
                "message": "Question text is required",
            }, status=status.HTTP_400_BAD_REQUEST)

        if not request.data.get("input_type"):
            return Response({
                "message": "Input type is required",
            }, status=status.HTTP_400_BAD_REQUEST)

        input_type_choice = ["text", "number", "mcq"]

        if request.data.get("input_type") not in input_type_choice:
            return Response({
                "message": "Invalid input type",
            }, status=status.HTTP_400_BAD_REQUEST)

        question = Question.objects.filter(question_text=request.data.get("question_text")).first()
        if question:
            return Response({
                "message": "Question already exists",
            }, status=status.HTTP_400_BAD_REQUEST)


        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Question created successfully",
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Question creation failed",
            "errors": serializer.errors
        }, status=400)
    

class QuestionDetailAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference_id):
        try:
            question = Question.objects.get(reference_id=reference_id)
        except Question.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = QuestionSerializer(question)
        return Response({
            "message": "Question fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

class QuestionUpdateAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, reference_id):
        try:
            question = Question.objects.get(reference_id=reference_id)
        except Question.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = QuestionSerializer(question, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Question updated successfully",
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Question update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class QuestionDeleteAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, reference_id):
        try:
            question = Question.objects.get(reference_id=reference_id)
        except Question.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        question.delete()
        return Response({
            "message": "Deleted",
        }, status=status.HTTP_200_OK)
    
class OptionListAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        options = Option.objects.all()
        serializer = OptionSerializer(options, many=True)
        return Response({
            "message": "Options fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

class OptionCreateAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = OptionSerializer(data=request.data)

        if not request.data.get("question"):
            return Response({
                "message": "Question is required",
            }, status=status.HTTP_400_BAD_REQUEST)

        if not request.data.get("option_text"):
            return Response({
                "message": "Option text is required",
            }, status=status.HTTP_400_BAD_REQUEST)

        option = Option.objects.filter(option_text=request.data.get("option_text")).first()
        if option:
            return Response({
                "message": "Option already exists",
            }, status=status.HTTP_400_BAD_REQUEST)

        question = Question.objects.filter(reference_id=request.data.get("question")).first()
        if not question:
            return Response({
                "message": "Question not found",
            }, status=status.HTTP_404_NOT_FOUND)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Option created successfully",
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Option creation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    
class OptionDetailAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference_id):
        try:
            option = Option.objects.get(reference_id=reference_id)
        except Option.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = OptionSerializer(option)
        return Response(serializer.data)
    
    
class OptionUpdateAPIView(APIView): 
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, reference_id):
        try:
            option = Option.objects.get(reference_id=reference_id)
        except Option.DoesNotExist:
            return Response({"error": "Option not found"}, status=404)        
        
        serializer = OptionSerializer(option, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Option updated successfully",
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Option update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    

class OptionDeleteAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, reference_id):
        try:
            option = Option.objects.get(reference_id=reference_id)
        except Option.DoesNotExist:
            return Response({"error": "Option not found"}, status=404)

        option.delete()
        return Response({"message": "Deleted"}, status=status.HTTP_200_OK)


class AssessmentTypeQuestionsAPIView(APIView):
    """
    GET /health/assessment-types/<reference_id>/questions/

    Returns all sections (with questions and options) belonging to the given assessment type.
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference_id):
        try:
            assessment_type = AssessmentType.objects.get(reference_id=reference_id)
        except AssessmentType.DoesNotExist:
            return Response({"message": "Assessment type not found"}, status=status.HTTP_404_NOT_FOUND)

        sections_data = []
        sections = assessment_type.sections.filter().prefetch_related("question_set__options").all()

        for section in sections:
            questions_data = []
            for question in section.question_set.all():
                options = []
                if question.input_type == "mcq":
                    options = [
                        {"option_id": str(opt.reference_id), "option_text": opt.option_text}
                        for opt in question.options.all()
                    ]
                questions_data.append({
                    "question_id": str(question.reference_id),
                    "question_text": question.question_text,
                    "input_type": question.input_type,
                    "options": options,
                })

            sections_data.append({
                "section_id": str(section.reference_id),
                "is_draft": section.is_draft,
                "name": section.name,
                "questions": questions_data,
            })

        return Response({
            "message": "Assessment questions fetched successfully",
            "data": {
                "assessment_type_id": str(assessment_type.reference_id),
                "name": assessment_type.name,
                "description": assessment_type.description,
                "sections": sections_data,
            }
        }, status=status.HTTP_200_OK)


class SectionWithQuestionsCreateAPIView(APIView):
    """
    Single endpoint to create a section along with its questions and options.

    POST /health/sections/create-with-questions/

    Request body:
    {
        "name": "Personal Information",
        "is_draft": true,
        "assessment_type": "<uuid>",   // optional
        "questions": [
            {
                "question_text": "What is your age?",
                "input_type": "number"
            },
            {
                "question_text": "Do you smoke?",
                "input_type": "mcq",
                "options": ["Yes", "No", "Occasionally"]
            }
        ]
    }
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SectionWithQuestionsSerializer(data=request.data)

        if serializer.is_valid():
            section = serializer.save()

            questions = Question.objects.filter(section=section).prefetch_related("options")
            questions_data = []
            for q in questions:
                options = [
                    {"reference_id": str(opt.reference_id), "option_text": opt.option_text}
                    for opt in q.options.all()
                ]

                questions_data.append({
                    "reference_id": str(q.reference_id),
                    "question_text": q.question_text,
                    "input_type": q.input_type,
                    "options": options,
                })

            return Response({
                "message": "Section created successfully",
                "data": {
                    "section_id": str(section.reference_id),
                    "is_draft": section.is_draft,
                    "name": section.name,
                    "questions": questions_data,
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Validation failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class AssessmentTypeWithSectionsCreateAPIView(APIView):
    """
    Single endpoint to create a full assessment type with sections, questions, and options.

    POST /health/assessment-types/create-with-sections/

    Request body:
    {
        "name": "General Health Assessment",
        "description": "...",
        "sections": [
            {
                "name": "Personal Info",
                "questions": [
                    { "question_text": "Your age?", "input_type": "number" },
                    { "question_text": "Do you smoke?", "input_type": "mcq", "options": ["Yes", "No", "Sometimes"] }
                ]
            },
            {
                "name": "Lifestyle",
                "questions": [
                    { "question_text": "Describe your diet", "input_type": "text" }
                ]
            }
        ]
    }
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AssessmentTypeWithSectionsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        assessment_type = serializer.save()

        # Build response
        sections_data = []
        for section in assessment_type.sections.prefetch_related("question_set__options").all():
            questions_data = []
            for q in section.question_set.all():
                options = [
                    {"reference_id": str(opt.reference_id), "option_text": opt.option_text}
                    for opt in q.options.all()
                ]
                questions_data.append({
                    "reference_id": str(q.reference_id),
                    "question_text": q.question_text,
                    "input_type": q.input_type,
                    "options": options,
                })
            sections_data.append({
                "reference_id": str(section.reference_id),
                "name": section.name,
                "questions": questions_data,
            })

        return Response({
            "message": "Assessment type created successfully",
            "data": {
                "reference_id": str(assessment_type.reference_id),
                "name": assessment_type.name,
                "description": assessment_type.description,
                "sections": sections_data,
            }
        }, status=status.HTTP_201_CREATED)




class SectionWithQuestionsUpdateAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        try:
            section = Section.objects.get(reference_id=request.data.get("section_id"))
        except Section.DoesNotExist:
            return Response({"message": "Section not found"}, status=404)

        serializer = SectionWithQuestionsUpdateSerializer(
            instance=section,
            data=request.data
        )

        if serializer.is_valid():
            section = serializer.save()

            return Response({
                "message": "Section updated successfully",
                "data": {
                    "reference_id": str(section.reference_id),
                    "name": section.name
                }
            })

        return Response(serializer.errors, status=400)


class AllAssessmentTypesFullTreeAPIView(APIView):
    """
    GET /health/assessment-types/full-tree/

    Returns every assessment type with its sections, and every
    section with its questions (and options for MCQ questions).

    Response shape:
    {
        "message": "...",
        "total": <int>,
        "data": [
            {
                "reference_id": "<uuid>",
                "name": "General Health Assessment",
                "description": "...",
                "sections": [
                    {
                        "reference_id": "<uuid>",
                        "name": "Personal Information",
                        "questions": [
                            {
                                "reference_id": "<uuid>",
                                "question_text": "What is your age?",
                                "input_type": "number",
                                "options": []
                            },
                            ...
                        ]
                    },
                    ...
                ]
            },
            ...
        ]
    }
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        assessment_types = (
            AssessmentType.objects
            .prefetch_related(
                models.Prefetch(
                    "sections",
                    queryset=Section.objects.filter(is_draft=False).prefetch_related("question_set__options")
                )
            )
            .all()
        )
        serializer = AssessmentTypeFullTreeSerializer(assessment_types, many=True)
        return Response({
            "message": "All assessment types with sections and questions fetched successfully",
            "total": assessment_types.count(),
            "data": serializer.data,
        }, status=status.HTTP_200_OK)