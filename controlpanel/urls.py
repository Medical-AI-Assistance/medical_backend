from django.urls import path
from controlpanel.views import views_user_management, views_dashboard

app_name = 'controlpanel'

urlpatterns = [
    path('dashboard/stats/', views_dashboard.DashboardStatsAPIView.as_view(), name='dashboard-stats'),

    path('users/', views_user_management.UserListAPIView.as_view(), name='user-list'),
    path('users/create/', views_user_management.UserCreateAPIView.as_view(), name='user-create'),
    path('users/<uuid:reference_id>/ban-unban/', views_user_management.UserBanAPIView.as_view(), name='user-ban-unban'),
    path('users/<uuid:reference_id>/admin-rights/', views_user_management.UserAdminRightsAPIView.as_view(), name='user-admin-rights'),
]
 