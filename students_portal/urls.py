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
    path('timetable/', views.timetable_view, name='timetable'),
    path('student_timetable/', views.student_timetable , name='student_timetable'),


    path('promote-students/', views.promote_students, name='promote_students'),
    path('fee-history/', views.student_fee_history, name='student_fee_history'),
    
    path('comments/', views.student_comments, name='student_comments'),
    path('admins/comments/', views.admin_comment_dashboard, name='admin_comment_dashboard'),
    path('admins/comments/<int:comment_id>/', views.admin_comment_response, name='admin_comment_response'),

    path('lecturer/units/', views.unit_students, name='lecturer_unit_students'),
    path('lecturer/units/<int:unit_allocation_id>/', views.unit_students, name='lecturer_unit_students_detail'),
    path('lecturer/notes/', views.upload_lecture_notes, name='upload_lecture_notes'),
    path('lecturer/notes/<int:unit_allocation_id>/', views.upload_lecture_notes, name='upload_lecture_notes_unit'),
    path('lecturer/notes/delete/<int:note_id>/', views.delete_lecture_note, name='delete_lecture_note'),
    path('student/notes/', views.student_view_notes, name='student_view_notes'),

    # Lecturer URLs
    path('lecturer/attendance/', views.lecturer_attendance_view, name='lecturer_attendance_view'),
    
    path('lecturer/attendance/unit/<int:unit_allocation_id>/', views.lecturer_unit_attendance, name='lecturer_unit_attendance'),
    
    # Student URLs
    path('student/attendance/', views.student_attendance_view, name='student_attendance_view'),
    
    path('student/attendance/sign/<int:unit_allocation_id>/', views.student_sign_attendance, name='student_sign_attendance'),

     path('lecturer/attendance/update/<int:unit_allocation_id>/<int:week>/', views.update_attendance,name='update_attendance'),

     path('student/attendance/history/<int:unit_allocation_id>/',views.student_attendance_history, name='student_attendance_history'),
     path('lecturer/units/<int:unit_allocation_id>/qr/', views.lecturer_generate_qr, name='lecturer_generate_qr'),
     path('attendance/scan/', views.student_scan_qr, name='student_scan_qr'),
     # Unit Allocation URLs
     path('unit-allocation/', views.unit_allocation_view, name='unit_allocation'),
    path('special-exam-application/', views.special_exam_application, name='special_exam_application'),
     path('verify-exam-payment/', views.verify_exam_payment, name='verify_exam_payment'),

     path('hostel/allocate/', views.allocate_hostel, name='allocate_hostel'),
    path('hostel/get-student-details/', views.get_student_details, name='get_student_details'),
    path('hostel/get-available-rooms/', views.get_available_rooms, name='get_available_rooms'),
    path('hostel/get-available-beds/', views.get_available_beds, name='get_available_beds'),
    path('hostel/get-current-year/', views.get_current_year, name='get_current_year'),
    path('hostel-explorer/', views.HostelAllocationExplorer.as_view(), name='hostel_allocation_explorer'),
    path('programme-units/', views.ProgrammeUnitExplorer.as_view(), name='programme_unit_explorer'),
    path('programme/<int:programme_id>/year/<int:year_of_study>/semester/<int:semester>/unit/<int:unit_id>/pdf/', 
     views.UnitStudentListPDFView.as_view(), name='unit_student_list_pdf'),
    path('hep-support/', views.help_support, name='help_support'),
    path('settings/', views.settings_view, name='settings_view'),
    path('virtual-assistant/', views.virtual_assistant, name='virtual_assistant'),
    path('process-query/', views.process_assistant_query, name='process_assistant_query'),
    path('forum/', views.discussion_forum, name='discussion_forum'),
    path('forum/group/<int:group_id>/', views.group_chat, name='group_chat'),
    path('forum/create/', views.create_group, name='create_group'),
    path('forum/join/<int:group_id>/', views.join_group, name='join_group'),
    path('forum/send/<int:group_id>/', views.send_message, name='send_message'),
    

]