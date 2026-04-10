from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core import permissions
from core.authentication import CookieJWTAuthentication
from openai import OpenAI
from django.conf import settings
from healthassessment.models import Question, Answer, AssessmentSession
from healthassessment.serializers import (
    SectionSerializer,
    QuestionSerializer,
    OptionSerializer,
    AnswerSerializer
)
import json

class AnswerSubmitAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        answers = request.data.get("answers", [])

        if not answers:
            return Response({"error": "No answers provided"}, status=400)

        # Create new session
        session = AssessmentSession.objects.create(
            user=request.user
        )

        answer_objects = []

        for item in answers:

            try:
                question = Question.objects.get(
                    reference_id=item.get("reference_id")
                )
            except Question.DoesNotExist:
                continue

            answer_objects.append(
                Answer(
                    session=session,
                    user=request.user,
                    question=question,
                    answer_text=item.get("answer", "")
                )
            )

        Answer.objects.bulk_create(answer_objects)

        return Response({
            "message": "Answers submitted successfully",
            "session_id": session.id
        })


    
class UserAnswerListAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        session = AssessmentSession.objects.filter(
            user=request.user
        ).order_by("-created_at").first()

        answers = session.answers.select_related("question")

        if not answers.exists():
            return Response({"error": "No answers in session"}, status=400)

        data = []

        for ans in answers:
            data.append({
                "question": ans.question.question_text,
                "answer": ans.answer_text
            })

        return Response(data)


class DiagnoseAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        session_id = request.data.get("session_id")

        if not session_id:
            return Response({"error": "session_id required"}, status=400)

        try:
            session = AssessmentSession.objects.get(
                id=session_id,
                user=request.user
            )
        except AssessmentSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=404)

        answers = session.answers.select_related("question")

        prompt = "User Health Data:\n\n"

        for ans in answers:
            prompt += f"{ans.question.question_text}: {ans.answer_text}\n"

        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=settings.NVIDIA_API_KEY
        )

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a medical risk assessment assistant.\n"
                        "Return ONLY valid JSON in this exact format:\n\n"
                        "{\n"
                        '  "risk_level": "Low | Medium | High",\n'
                        '  "concerns": [\n'
                        '    {\n'
                        '      "area": "string",\n'
                        '      "description": "string",\n'
                        '      "what_to_watch": "string"\n'
                        "    }\n"
                        "  ],\n"
                        '  "recommendations": [\n'
                        '    {\n'
                        '      "category": "string",\n'
                        '      "action": "string",\n'
                        '      "goal": "string"\n'
                        "    }\n"
                        "  ]\n"
                        "}\n\n"
                        "Do NOT include markdown, tables, or explanations outside JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=600
        )

        result = completion.choices[0].message.content
        try:
            parsed_result = json.loads(result)
        except json.JSONDecodeError:
            return Response({
                "error": "AI response not in valid JSON format",
                "raw": result
            }, status=500)
        return Response({
            "session_id": session_id,
            "assessment": parsed_result
        })