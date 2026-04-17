from rest_framework.views import APIView
from rest_framework.response import Response
from core import permissions
from core.authentication import CookieJWTAuthentication
from openai import OpenAI
from django.conf import settings
from healthassessment.models import Question, Answer, AssessmentSession, AssessmentType, DiagnosisReport
from django.db.models import Prefetch
import json

class AnswerSubmitAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        answers = request.data.get("answers", [])
        assessment_type_id = request.data.get("assessment_type_id")

        if not answers:
            return Response({"error": "No answers provided"}, status=400)

        assessment_type = None
        if assessment_type_id:
            try:
                assessment_type = AssessmentType.objects.get(reference_id=assessment_type_id)
            except AssessmentType.DoesNotExist:
                return Response({"error": "Invalid assessment_type_id"}, status=400)

        # Validate all question IDs up front before touching the DB
        missing_id_errors = [
            {
                "index": i,
                "error": "question_id is required but was not provided"
            }
            for i, item in enumerate(answers)
            if not item.get("question_id")
        ]
        if missing_id_errors:
            return Response({"errors": missing_id_errors}, status=400)

        question_ids = [item["question_id"] for item in answers]

        questions_map = {
            str(q.reference_id): q
            for q in Question.objects.filter(reference_id__in=question_ids)
        }

        invalid_id_errors = [
            {
                "index": i,
                "question_id": item["question_id"],
                "error": f"No question found with reference_id '{item['question_id']}'"
            }
            for i, item in enumerate(answers)
            if item["question_id"] not in questions_map
        ]
        if invalid_id_errors:
            return Response({"errors": invalid_id_errors}, status=400)

        # Create new session
        session = AssessmentSession.objects.create(
            user=request.user,
            assessment_type=assessment_type
        )

        answer_objects = [
            Answer(
                session=session,
                user=request.user,
                assessment_type=assessment_type,
                question=questions_map[item["question_id"]],
                answer_text=item.get("answer", "")
            )
            for item in answers
        ]

        Answer.objects.bulk_create(answer_objects)

        return Response({
            "message": "Answers submitted successfully",
            "session_id": str(session.reference_id)
        })


    
class UserAnswerListAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, assessment_type_id):
        
        sessions_query = AssessmentSession.objects.filter(user=request.user).order_by("-created_at")

        if assessment_type_id:
            try:
                sessions_query = sessions_query.filter(assessment_type__reference_id=assessment_type_id)
            except ValueError:
                return Response({"error": "Invalid assessment_type"}, status=400)

        if not sessions_query.exists():
            return Response([])

        sessions = sessions_query.prefetch_related(
            Prefetch("answers", queryset=Answer.objects.select_related("question", "question__section", "session__assessment_type"))
        )

        response_data = []

        for session in sessions:
            answers = session.answers.all()

            if not answers:
                continue

            assessment_type_name = session.assessment_type.name if session.assessment_type else "Unknown Assessment"

            sections_dict = {}

            for ans in answers:
                section_name = ans.question.section.name if ans.question.section else "Other"
                
                if section_name not in sections_dict:
                    sections_dict[section_name] = []
                
                sections_dict[section_name].append({
                    "question": ans.question.question_text,
                    "answer": ans.answer_text
                })

            sections_list = [
                {"section_name": section, "questions": questions}
                for section, questions in sections_dict.items()
            ]

            response_data.append({
                "session_id": str(session.reference_id),
                "assessment_type": assessment_type_name,
                "created_at": session.created_at,
                "sections": sections_list
            })

        return Response(response_data)


class AssessmentTypeSessionsAPIView(APIView):
    """
    GET /health/assessment-types/<reference_id>/sessions/
    Lists all sessions for a given assessment type belonging to the logged-in user,
    each session grouped with its answers.
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference_id):
        try:
            assessment_type = AssessmentType.objects.get(reference_id=reference_id)
        except (AssessmentType.DoesNotExist, ValueError):
            return Response({"error": "Assessment type not found"}, status=404)

        sessions = AssessmentSession.objects.filter(
            user=request.user,
            assessment_type=assessment_type
        ).order_by("-created_at")

        data = []
        for session in sessions:
            answers = Answer.objects.filter(
                session=session,
                assessment_type=assessment_type
            ).select_related("question")

            data.append({
                "session_id": str(session.reference_id),
                "created_at": session.created_at,
                "answers": [
                    {
                        "question": ans.question.question_text,
                        "answer": ans.answer_text
                    }
                    for ans in answers
                ]
            })

        return Response({
            "assessment_type": assessment_type.name,
            "total_sessions": len(data),
            "sessions": data
        })


class DiagnosisHistoryAPIView(APIView):
    """
    GET /health/diagnose/history/<uuid:assessment_type_id>/
    Lists all auto-generated diagnostic reports for the user's sessions matching the given assessment type.
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, assessment_type_id):
        try:
            assessment_type = AssessmentType.objects.get(reference_id=assessment_type_id)
        except (AssessmentType.DoesNotExist, ValueError):
            return Response({"error": "Assessment type not found"}, status=404)

        # Get all sessions matching user and assessment_type that also have an AI response
        sessions = AssessmentSession.objects.filter(
            user=request.user,
            assessment_type=assessment_type,
            diagnosis_reports__isnull=False
        ).prefetch_related("diagnosis_reports").order_by("-created_at").distinct()

        history_data = []
        for session in sessions:
            reports = session.diagnosis_reports.order_by("-created_at")
            report_list = []
            for report in reports:
                report_list.append({
                    "id": str(report.reference_id),
                    "created_at": getattr(report, 'created_at', session.created_at),
                    "risk_level": report.risk_level,
                    "problems": report.problems,
                    "recommendations": report.recommendations
                })
                
            history_data.append({
                "session_id": str(session.reference_id),
                "created_at": session.created_at,
                "reports": report_list
            })

        return Response({
            "assessment_type_id": str(assessment_type.reference_id),
            "assessment_type": assessment_type.name,
            "total_sessions_with_reports": len(history_data),
            "history": history_data
        })


ASSESSMENT_JSON_SCHEMA = (
    "Return ONLY valid JSON in this exact format — no markdown, no extra text:\n\n"
    "{\n"
    '  "risk_level": "Low | Medium | High",\n'
    '  "problems": [\n'
    '    {\n'
    '      "name": "string",\n'
    '      "cause": "string",\n'
    '      "consequence": "string",\n'
    '      "remedy": "string"\n'
    "    }\n"
    "  ],\n"
    '  "recommendations": [\n'
    '    {\n'
    '      "category": "string",\n'
    '      "action": "string",\n'
    '      "goal": "string"\n'
    "    }\n"
    "  ]\n"
    "}"
)


class DiagnoseAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")
        assessment_type_id = request.data.get("assessment_type_id")

        if not session_id:
            return Response({"error": "session_id is required"}, status=400)

        if not assessment_type_id:
            return Response({"error": "assessment_type_id is required"}, status=400)

        try:
            assessment_type = AssessmentType.objects.get(reference_id=assessment_type_id)
        except (AssessmentType.DoesNotExist, ValueError):
            return Response({"error": "Invalid assessment_type_id"}, status=400)

        try:
            session = AssessmentSession.objects.get(
                reference_id=session_id,
                user=request.user
            )
        except (AssessmentSession.DoesNotExist, ValueError):
            return Response({"error": "Session not found"}, status=404)

        if session.assessment_type_id != assessment_type.id:
            return Response(
                {
                    "error": "assessment_type_id does not match the session's assessment type",
                    "session_assessment_type": session.assessment_type.name if session.assessment_type else None,
                },
                status=400
            )

        answers = Answer.objects.filter(
            session=session,
            assessment_type=assessment_type
        ).select_related("question")

        # Print the answers for debugging with the actual question and answer and also print the assessment type
        for ans in answers:
            print(f"Question: {ans.question.question_text}, Answer: {ans.answer_text}")

        if not answers.exists():
            return Response({"error": "No answers found for this session and assessment type"}, status=400)

        user_data = "User Health Data:\n\n"
        for ans in answers:
            user_data += f"{ans.question.question_text}: {ans.answer_text}\n"

        system_prompt = (
            f"You are a medical risk assessment specialist. "
            f"Focus your analysis and recommendations specifically on identifying risks related to '{assessment_type.name}' based on the user's data.\n\n"
            f"{ASSESSMENT_JSON_SCHEMA}"
        )

        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=settings.NVIDIA_API_KEY
        )

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_data}
            ],
            temperature=0.7,
            max_tokens=3000
        )

        result = completion.choices[0].message.content

        # Sanitize the result to remove markdown code block framing if the AI outputs it
        cleaned_result = result.strip()
        if cleaned_result.startswith('```'):
            lines = cleaned_result.split('\n')
            if len(lines) > 0 and lines[0].startswith('```'):
                lines = lines[1:]
            if len(lines) > 0 and lines[-1].strip() == '```':
                lines = lines[:-1]
            cleaned_result = '\n'.join(lines).strip()

        try:
            parsed_result = json.loads(cleaned_result)
        except json.JSONDecodeError:
            return Response({
                "error": "AI response was not valid JSON",
                "raw": result,
                "cleaned": cleaned_result
            }, status=500)

        # Save diagnosis to database as a new record
        DiagnosisReport.objects.create(
            session=session,
            risk_level=parsed_result.get("risk_level", ""),
            problems=parsed_result.get("problems", []),
            recommendations=parsed_result.get("recommendations", [])
        )

        return Response({
            "session_id": str(session.reference_id),
            "assessment_type": session.assessment_type.name if session.assessment_type else None,
            "assessment": parsed_result
        })

