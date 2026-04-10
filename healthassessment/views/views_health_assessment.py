from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from django.conf import settings
from healthassessment.models import Section, Question, Option, Answer
from healthassessment.serializers import (
    SectionSerializer,
    QuestionSerializer,
    OptionSerializer,
    AnswerSerializer
)


class AnswerSubmitAPIView(APIView):

    def post(self, request):

        answers = request.data.get("answers", [])

        saved = []

        for item in answers:
            Answer.objects.create(
                user=request.user,
                question_id=item["question_id"],
                answer_text=item["answer"]
            )
            saved.append(item["question_id"])

        return Response({
            "message": "Answers submitted",
            "questions": saved
        })
    
class UserAnswerListAPIView(APIView):

    def get(self, request):

        answers = Answer.objects.filter(user=request.user)
        serializer = AnswerSerializer(answers, many=True)

        return Response(serializer.data)

class DiagnoseAPIView(APIView):

    def post(self, request):
        message = request.data.get("message")

        if not message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=settings.NVIDIA_API_KEY
        )

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical assistant helping users understand possible illnesses based on symptoms."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.7,
            max_tokens=500
        )

        result = completion.choices[0].message.content

        print("AI Response:", result)

        return Response({
            "response": result
        })