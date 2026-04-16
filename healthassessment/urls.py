from django.urls import path
from . import views

app_name = 'users_auth'

urlpatterns = [

    path("health/assessment-types/", views.AssessmentTypeListAPIView.as_view(), name="assessment-type-list"),
    path("health/assessment-types/create/", views.AssessmentTypeCreateAPIView.as_view(), name="assessment-type-create"),
    path("health/assessment-types/bulk-create/", views.AssessmentTypeWithSectionsCreateAPIView.as_view(), name="assessment-type-bulk-create"),
    path("health/assessment-types/<uuid:reference_id>/", views.AssessmentTypeDetailAPIView.as_view(), name="assessment-type-detail"),
    path("health/assessment-types/<uuid:reference_id>/questions/", views.AssessmentTypeQuestionsAPIView.as_view(), name="assessment-type-questions"),
    path("health/assessment-types/<uuid:reference_id>/sessions/", views.AssessmentTypeSessionsAPIView.as_view(), name="assessment-type-sessions"),
    path("health/assessment-types/<uuid:reference_id>/update/", views.AssessmentTypeUpdateAPIView.as_view(), name="assessment-type-update"),
    path("health/assessment-types/<uuid:reference_id>/delete/", views.AssessmentTypeDeleteAPIView.as_view(), name="assessment-type-delete"),


    path("health/sections/", views.SectionListAPIView.as_view(), name="section-list"),
    path("health/assessment-type/<uuid:reference_id>/sections/", views.AssessmentTypeSectionsAPIView.as_view(), name="assessment-type-sections"),
    path("health/sections/create/", views.SectionCreateAPIView.as_view(), name="section-create"),
    path("health/sections/bulk-create/", views.SectionWithQuestionsCreateAPIView.as_view(), name="section-bulk-create"),
    # path("health/sections/<uuid:reference_id>")
    path("health/sections/bulk-update/", views.SectionWithQuestionsUpdateAPIView.as_view(), name="section-bulk-update"),
    path("health/sections/<uuid:reference_id>/", views.SectionDetailAPIView.as_view(), name="section-detail"),
    path("health/sections/<uuid:reference_id>/update/", views.SectionUpdateAPIView.as_view(), name="section-update"),
    path("health/sections/<uuid:reference_id>/delete/", views.SectionDeleteAPIView.as_view(), name="section-delete"),


    path("health/questions/", views.QuestionListAPIView.as_view(), name="question-list"),
    path("health/questions/create/", views.QuestionCreateAPIView.as_view(), name="question-create"),
    path("health/questions/<uuid:reference_id>/", views.QuestionDetailAPIView.as_view(), name="question-detail"),
    path("health/questions/<uuid:reference_id>/update/", views.QuestionUpdateAPIView.as_view(), name="question-update"),
    path("health/questions/<uuid:reference_id>/delete/", views.QuestionDeleteAPIView.as_view(), name="question-delete"),

    path("health/options/", views.OptionListAPIView.as_view(), name="option-list"),
    path("health/options/create/", views.OptionCreateAPIView.as_view(), name="option-create"),
    path("health/options/<uuid:reference_id>/", views.OptionDetailAPIView.as_view(), name="option-detail"),
    path("health/options/<uuid:reference_id>/update/", views.OptionUpdateAPIView.as_view(), name="option-update"),
    path("health/options/<uuid:reference_id>/delete/", views.OptionDeleteAPIView.as_view(), name="option-delete"),

    path("health/answers/submit/", views.AnswerSubmitAPIView.as_view(), name="answer-submit"),
    path("health/answers/list/", views.UserAnswerListAPIView.as_view(), name="user-answers"),

    path('health/general-health-assessment/', views.DiagnoseAPIView.as_view(), name='health-assessment'),
    path('health/cardiovascular-risk-assessment/', views.DiagnoseCardiovascularAPIView.as_view(), name='cardiovascular-risk-assessment'),
    path('health/diabetes-risk-assessment/', views.DiagnoseDiabetesAPIView.as_view(), name='diabetes-risk-assessment'),
    path('health/respiratory-risk-assessment/', views.DiagnoseRespiratoryAPIView.as_view(), name='respiratory-risk-assessment'),
]