from django.urls import path
from . import views

app_name = 'users_auth'

urlpatterns = [
    # path('health/questions/', views.DiagnoseAPIView.as_view(), name='health-questions'),
    # path('health/submit-answers/', views.DiagnoseAPIView.as_view(), name='submit-answers'),
    # path('health/assessment/results/', views.DiagnoseAPIView.as_view(), name='result-assessment'),
    path('health/assessment/', views.DiagnoseAPIView.as_view(), name='health-assessment'),


    path("health/sections/", views.SectionListAPIView.as_view(), name="section-list"),
    path("health/sections/create/", views.SectionCreateAPIView.as_view(), name="section-create"),
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
]