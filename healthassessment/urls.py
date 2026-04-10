from django.urls import path
from . import views

app_name = 'users_auth'

urlpatterns = [
    path('health/questions/', views.DiagnoseAPIView.as_view(), name='health-questions'),
    path('health/submit-answers/', views.DiagnoseAPIView.as_view(), name='submit-answers'),
    path('health/assessment/', views.DiagnoseAPIView.as_view(), name='health-assessment'),
    path('health/assessment/results/', views.DiagnoseAPIView.as_view(), name='result-assessment'),
]