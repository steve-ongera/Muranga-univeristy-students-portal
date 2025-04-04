from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.registration_view, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('profile/', views.student_profile_view, name='student_profile'),
    # Add paths for your dashboards
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('lecturer/dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('mainadmin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('finance/dashboard/', views.finance_dashboard, name='finance_dashboard'),
    path('api/gender-distribution/', views.gender_distribution_api, name='gender_distribution_api'),

    #students
    path('database_students_list/', views.database_students_list, name='database_students_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/update/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),

    #seachings
    path('search-student-data/', views.search_student_data, name='search_student_data'),
    #path('student/<int:student_id>/academic-record/', views.student_academic_record, name='student_academic_record'),

    path('lecturers/', views.lecturer_list, name='lecturer_list'),
    path('lecturers/add/', views.lecturer_create, name='lecturer_create'),
    path('lecturers/<int:pk>/', views.lecturer_detail, name='lecturer_detail'),
    path('lecturers/<int:pk>/edit/', views.lecturer_update, name='lecturer_update'),
    path('lecturers/<int:pk>/delete/', views.lecturer_delete, name='lecturer_delete'),

    path('enrollment/', views.unit_enrollment, name='unit_enrollment'),
    path('enrollment/drop/<int:enrollment_id>/', views.drop_unit, name='drop_unit'),
    path('report/', views.report_for_semester, name='report_for_semester'),
    path('results/', views.student_results_view, name='academic_results'),
    path('download-transcript/', views.download_transcript, name='download_transcript'),

    #admin to enter marks urls
    path('enter-grades/', views.enter_student_grades, name='enter-grades'),
    path('search-student/', views.search_student, name='search-student'),
    path('save_student_grades/', views.save_student_grades, name='save-student-grades'),

    #acdemics
    path('student/<int:student_id>/progress/', views.student_progress_report, name='student_progress'),
    path('student/<int:student_id>/transcript/', views.student_official_transcript, name='student_transcript'),
    path('api/student/<int:student_id>/progress/', views.api_student_progress, name='api_student_progress'),

    path('programmes/', views.programme_list, name='programme_list'),
    path('programmes/<int:programme_id>/', views.programme_detail, name='programme_detail'),

    path('promote-students/', views.promote_students, name='promote_students'),
   
 

]