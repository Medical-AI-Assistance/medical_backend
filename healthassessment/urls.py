from django.urls import path
from . import views

app_name = 'users_auth'

urlpatterns = [
    path('health/questions/', views.DiagnoseAPIView.as_view(), name='health-questions'),
    path('health/submit-answers/', views.DiagnoseAPIView.as_view(), name='submit-answers'),
    path('health/assessment/', views.DiagnoseAPIView.as_view(), name='health-assessment'),
    path('health/assessment/results/', views.DiagnoseAPIView.as_view(), name='result-assessment'),


    path("sections/", views.SectionListAPIView.as_view(), name="section-list"),
    path("sections/create/", views.SectionCreateAPIView.as_view(), name="section-create"),
    path("sections/<int:pk>/", views.SectionDetailAPIView.as_view(), name="section-detail"),
    path("sections/<int:pk>/update/", views.SectionUpdateAPIView.as_view(), name="section-update"),
    path("sections/<int:pk>/delete/", views.SectionDeleteAPIView.as_view(), name="section-delete"),
    

    path("questions/", views.QuestionListAPIView.as_view(), name="question-list"),
    path("questions/create/", views.QuestionCreateAPIView.as_view(), name="question-create"),
    path("questions/<int:pk>/", views.QuestionDetailAPIView.as_view(), name="question-detail"),
    path("questions/<int:pk>/update/", views.QuestionUpdateAPIView.as_view(), name="question-update"),
    path("questions/<int:pk>/delete/", views.QuestionDeleteAPIView.as_view(), name="question-delete"),
    

    path("options/", views.OptionListAPIView.as_view(), name="option-list"),
    path("options/create/", views.OptionCreateAPIView.as_view(), name="option-create"),
    path("options/<int:pk>/", views.OptionDetailAPIView.as_view(), name="option-detail"),
    path("options/<int:pk>/update/", views.OptionUpdateAPIView.as_view(), name="option-update"),
    path("options/<int:pk>/delete/", views.OptionDeleteAPIView.as_view(), name="option-delete"),
    

    path("answers/submit/", views.AnswerSubmitAPIView.as_view(), name="answer-submit"),
    path("answers/", views.UserAnswerListAPIView.as_view(), name="user-answers"),

]