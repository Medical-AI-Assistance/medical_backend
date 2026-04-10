from uritemplate import partial
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from healthassessment.models import Section, Question, Option, Answer
from healthassessment.serializers import (
    SectionSerializer,
    QuestionSerializer,
    OptionSerializer,
    AnswerSerializer
)
from core import permissions
from core.authentication import CookieJWTAuthentication 


class SectionListAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sections = Section.objects.all()
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
    



class QuestionListAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        sections = Section.objects.all()

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


