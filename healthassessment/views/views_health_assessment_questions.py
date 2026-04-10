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


class SectionListAPIView(APIView):

    def get(self, request):
        sections = Section.objects.all()
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)
    

class SectionCreateAPIView(APIView):

    def post(self, request):
        serializer = SectionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
    

class SectionDetailAPIView(APIView):

    def get(self, request, reference_id):
        try:
            section = Section.objects.get(reference_id=reference_id)
        except Section.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = SectionSerializer(section)
        return Response(serializer.data)
    

class SectionUpdateAPIView(APIView):

    def put(self, request, reference_id):
        try:
            section = Section.objects.get(reference_id=reference_id)
        except Section.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = SectionSerializer(section, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)
    

class SectionDeleteAPIView(APIView):

    def delete(self, request, reference_id):
        try:
            section = Section.objects.get(reference_id=reference_id)
        except Section.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        section.delete()
        return Response({"message": "Deleted"})
    


# class QuestionListAPIView(APIView):

#     def get(self, request):
#         questions = Question.objects.all()
#         serializer = QuestionSerializer(questions, many=True)
#         return Response(serializer.data)
    

class QuestionCreateAPIView(APIView):

    def post(self, request):
        serializer = QuestionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
    

class QuestionDetailAPIView(APIView):

    def get(self, request, reference_id):
        try:
            question = Question.objects.get(reference_id=reference_id)
        except Question.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = QuestionSerializer(question)
        return Response(serializer.data)
    

class QuestionUpdateAPIView(APIView):

    def put(self, request, reference_id):
        try:
            question = Question.objects.get(reference_id=reference_id)
        except Question.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = QuestionSerializer(question, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)
    

class QuestionDeleteAPIView(APIView):

    def delete(self, request, reference_id):
        try:
            question = Question.objects.get(reference_id=reference_id)
        except Question.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        question.delete()
        return Response({"message": "Deleted"})
    
class OptionListAPIView(APIView):

    def get(self, request):
        options = Option.objects.all()
        serializer = OptionSerializer(options, many=True)
        return Response(serializer.data)
    

class OptionCreateAPIView(APIView):

    def post(self, request):
        serializer = OptionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
    
class OptionDetailAPIView(APIView):

    def get(self, request, reference_id):
        try:
            option = Option.objects.get(reference_id=reference_id)
        except Option.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = OptionSerializer(option)
        return Response(serializer.data)
    
class OptionUpdateAPIView(APIView):

    def put(self, request, reference_id):
        option = Option.objects.get(reference_id=reference_id)
        serializer = OptionSerializer(option, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)
    
class OptionDeleteAPIView(APIView):

    def delete(self, request, reference_id):
        option = Option.objects.get(reference_id=reference_id)
        option.delete()
        return Response({"message": "Deleted"})




class QuestionListAPIView(APIView):

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