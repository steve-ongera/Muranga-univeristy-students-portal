from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.registration_view, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    # Add paths for your dashboards
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('lecturer/dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('mainadmin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('finance/dashboard/', views.finance_dashboard, name='finance_dashboard'),
    path('api/gender-distribution/', views.gender_distribution_api, name='gender_distribution_api'),
    
]