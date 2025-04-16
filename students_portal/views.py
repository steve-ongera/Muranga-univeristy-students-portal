from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from .forms import *
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.cache import cache
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
Account = get_user_model()
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Count, Q
from datetime import datetime
import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import os
from django.db.models import Sum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import json




def login_view(request):
    """
    Handle login for all user types (students, lecturers, and admin/staff).
    Redirects to appropriate dashboard based on user_type.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', None)  # Optional for admin login
        
        # Try to authenticate with Django's auth system
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Check user_type from User model first
            if user.user_type == 'admin':
                return redirect('admin_dashboard')
            elif user.user_type == 'staff':
                return redirect('staff_dashboard')
            elif user.user_type == 'finance':
                return redirect('finance_dashboard')
            
            # For student/lecturer, verify against their respective models
            try:
                student = Student.objects.get(registration_number=username)
                # Update session with current student info
                request.session['user_type'] = 'student'
                request.session['student_id'] = student.id
                messages.success(request, "Logged in successfully to your account.")
                return redirect('student_dashboard')
            except Student.DoesNotExist:
                try:
                    lecturer = Lecturer.objects.get(staff_id=username)
                    # Update session with current lecturer info
                    request.session['user_type'] = 'lecturer'
                    request.session['lecturer_id'] = lecturer.id
                    return redirect('lecturer_dashboard')
                except Lecturer.DoesNotExist:
                    # Admin/staff users won't have student/lecturer records
                    if user.user_type in ['admin', 'staff', 'finance']:
                        return redirect(f'{user.user_type}_dashboard')
                    messages.error(request, "Account not linked to any profile.")
                    return redirect('login')
        else:
            # Authentication failed - provide appropriate error message
            error_message = "Invalid credentials."
            
            # Check if username exists in any system
            user_exists = User.objects.filter(username=username).exists()
            is_student = Student.objects.filter(registration_number=username).exists()
            is_lecturer = Lecturer.objects.filter(staff_id=username).exists()
            
            if user_exists:
                error_message = "Invalid password."
            elif is_student or is_lecturer:
                error_message = "No user account found for this ID. Please register first."
            else:
                error_message = "Invalid username. No matching account found."
            
            messages.error(request, error_message)
            return render(request, 'auth/login.html', {
                'username': username,
                'user_type': user_type
            })
    
    # If GET request, just show the login form
    return render(request, 'auth/login.html')

def custom_logout(request):
    logout(request)
    messages.error(request, "Logged out successfully!")
    return redirect('login')


#forgot password view 
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)

            # Generate reset password token and send email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            context = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http'
            }
            
            # Render both HTML and plain text versions of the email
            html_message = render_to_string('auth/reset_password_email.html', context)
            plain_message = strip_tags(html_message)
            
            to_email = email
            
            # Use EmailMultiAlternatives for sending both HTML and plain text
            email = EmailMultiAlternatives(
                mail_subject,
                plain_message,
                'noreply@yourdomain.com',
                [to_email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgot_password')
    return render(request, 'auth/forgot_password.html')



def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
                if len(password) < 6:
                    messages.error(request, 'Password must be at least 6 characters.')
                    return redirect('reset_password', uidb64=uidb64, token=token)

                user.set_password(password)
                user.last_password_change = timezone.now()
                user.save()
                messages.success(request, 'Password reset successful. You can now login with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect('reset_password', uidb64=uidb64, token=token)

        # GET request – render the form
        return render(request, 'auth/reset_password.html')
    else:
        messages.error(request, 'Invalid or expired reset link. Please try again.')
        return redirect('login')
    





def registration_view(request):
    """
    Handle user registration with user type and verification status
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')  # 'student' or 'lecturer'
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'auth/registration.html', {
                'username': username,
                'user_type': user_type,
                'first_name': first_name,
                'last_name': last_name
            })
        
        # Validate username exists in appropriate model and names match
        if user_type == 'student':
            try:
                student = Student.objects.get(registration_number=username)
                
                # Verify names match
                if (student.first_name.lower() != first_name.lower() or 
                    student.last_name.lower() != last_name.lower()):
                    messages.error(request, "Registration number does not match the provided names.")
                    return render(request, 'auth/registration.html', {
                        'username': username,
                        'user_type': user_type,
                        'first_name': first_name,
                        'last_name': last_name
                    })
                
                # Check if user already exists 
                if User.objects.filter(username=username).exists():
                    messages.error(request, "A user with this registration number already exists.")
                    return render(request, 'auth/registration.html', {
                        'username': username,
                        'user_type': user_type,
                        'first_name': first_name,
                        'last_name': last_name
                    })
                
                # Create new user with student type
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    user_type='student',
                    is_verified=True,  # Verified since we matched official records
                    first_name=student.first_name,
                    last_name=student.last_name,
                    email=student.email or ''
                )
                
                messages.success(request, f"Student account created successfully for {student.get_full_name()}.")
                return redirect('login')
                
            except Student.DoesNotExist:
                messages.error(request, "No student found with this registration number.")
                return render(request, 'auth/registration.html', {
                    'username': username,
                    'user_type': user_type,
                    'first_name': first_name,
                    'last_name': last_name
                })
                
        elif user_type == 'lecturer':
            try:
                lecturer = Lecturer.objects.get(staff_id=username)
                
                # Verify names match
                if (lecturer.first_name.lower() != first_name.lower() or 
                    lecturer.last_name.lower() != last_name.lower()):
                    messages.error(request, "Staff ID does not match the provided names.")
                    return render(request, 'auth/registration.html', {
                        'username': username,
                        'user_type': user_type,
                        'first_name': first_name,
                        'last_name': last_name
                    })
                
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    messages.error(request, "A user with this staff ID already exists.")
                    return render(request, 'auth/registration.html', {
                        'username': username,
                        'user_type': user_type,
                        'first_name': first_name,
                        'last_name': last_name
                    })
                
                # Create new user with lecturer type
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    user_type='lecturer',
                    is_verified=True,  # Verified since we matched official records
                    first_name=lecturer.first_name,
                    last_name=lecturer.last_name,
                    email=lecturer.email or ''
                )
                
                messages.success(request, f"Lecturer account created successfully for {lecturer.get_full_name()}.")
                return redirect('login')
                
            except Lecturer.DoesNotExist:
                messages.error(request, "No lecturer found with this staff ID.")
                return render(request, 'auth/registration.html', {
                    'username': username,
                    'user_type': user_type,
                    'first_name': first_name,
                    'last_name': last_name
                })
        
        else:
            messages.error(request, "Invalid user type selected.")
            return render(request, 'auth/registration.html', {
                'username': username,
                'first_name': first_name,
                'last_name': last_name
            })
    
    # If GET request, just show the registration form
    return render(request, 'auth/registration.html')

@login_required
def student_dashboard(request):
    """
    Dashboard view for students.
    Displays student profile information, academic details, current semester unit registrations,
    and current semester fee balance only.
    """
    # Check if user is a student
    if request.session.get('user_type') != 'student':
        messages.error(request, "You don't have access to the student dashboard.")
        return redirect('login')
    
    # Get student id from session
    student_id = request.session.get('student_id')
    
    try:
        # Fetch the student record with related programme
        student = Student.objects.select_related('programme').get(id=student_id)
        programme = student.programme
        
        # Get current semester
        current_semester = Semester.objects.filter(is_current=True).first()
        if not current_semester:
            current_semester = Semester.objects.order_by('-academic_year__start_date', '-start_date').first()
        
        # Get enrolled units for current semester
        enrolled_units = []
        session_progress = 0
        if current_semester:
            enrolled_units = StudentEnrollment.objects.filter(
                student=student,
                semester=current_semester
            ).select_related('programme_unit', 'programme_unit__unit')
            
            # Calculate session progress
            if current_semester.end_date and current_semester.start_date:
                today = datetime.now().date()
                total_days = (current_semester.end_date - current_semester.start_date).days
                days_passed = max(0, (today - current_semester.start_date).days)
                session_progress = min(100, round((days_passed / total_days) * 100)) if total_days > 0 else 0
        
        # ===== CURRENT SEMESTER FEE BALANCE =====
        current_balance = 0
        current_fee_record = None
        
        if current_semester:
            # Get the fee structure for current semester/year/programme
            current_fee_structure = FeesStructure.objects.filter(
                programme=programme,
                year_of_study=student.current_year,
                semester=student.current_semester,
                academic_year=current_semester.academic_year
            ).first()
            
            # Get the student's fee record for this structure if exists
            if current_fee_structure:
                current_fee_record = StudentFee.objects.filter(
                    student=student,
                    fee_structure=current_fee_structure
                ).first()
                
                if current_fee_record:
                    current_balance = current_fee_record.balance
        
        context = {
            'student': student,
            'programme': programme,
            'current_semester': current_semester,
            'enrolled_units': enrolled_units,
            'session_progress': session_progress,
            'current_balance': current_balance,
            'current_fee_record': current_fee_record,  # Pass the entire record for more details if needed
            'page_title': 'Student Dashboard',
        }
        
        return render(request, 'dashboards/student_dashborad_page.html', context)
    
    except Student.DoesNotExist:
        messages.error(request, "Student data profile not found. Please contact administration.")
        return redirect('login')
    

@login_required
def lecturer_dashboard(request):
    """
    Dashboard view for lecturers.
    Displays lecturer profile information, courses, schedule, and other academic details.
    """
    # Check if user is a lecturer
    if request.session.get('user_type') != 'lecturer':
        messages.error(request, "You don't have access to the lecturer dashboard.")
        return redirect('login')
    
    # Get lecturer id from session
    lecturer_id = request.session.get('lecturer_id')
    
    try:
        # Fetch the lecturer record
        lecturer = Lecturer.objects.get(id=lecturer_id)
        
        # Get current academic year and semester
        current_semester = Semester.objects.filter(is_current=True).first()
        current_year = current_semester.academic_year if current_semester else None
        
        # Fetch related department information
        department = lecturer.department
        
        
        # Get courses assigned to this lecturer for current semester
        # Get courses with proper student count annotation
        current_courses = UnitAllocation.objects.filter(
            lecturer=lecturer,
            semester=current_semester
        ).select_related(
            'programme_unit__unit',
            'programme_unit__programme'
        ).annotate(
            student_count=Count(
                'programme_unit__enrollments',
                filter=Q(programme_unit__enrollments__semester=current_semester),
                distinct=True
            )
        )
        
        # Get today's schedule
        today = timezone.now().date()
        today_weekday = today.weekday()  # Monday=0, Sunday=6
        
        today_schedule = ClassSchedule.objects.filter(
            unit_allocation__lecturer=lecturer,
            day_of_week=today_weekday,
            unit_allocation__semester=current_semester
        ).select_related(
            'unit_allocation__programme_unit__unit',
            'unit_allocation__programme_unit__programme'
        ).order_by('start_time')
        
        # Get pending tasks (example data - could be replaced with real task model)
        pending_tasks = [
            {
                'title': 'Grade Midterm Exams',
                'course': 'CS 401',
                'due': 'Due tomorrow',
                'priority': 'High'
            },
            {
                'title': 'Prepare Lecture Notes',
                'course': 'CS 402',
                'due': 'Due Friday',
                'priority': 'Medium'
            },
            {
                'title': 'Department Meeting',
                'course': '',
                'due': 'Tomorrow 10:00 AM',
                'priority': 'Low'
            }
        ]
        
        # Get department announcements
        announcements = Announcement.objects.filter(
            department=department,
            publish_date__lte=timezone.now()
        ).order_by('-publish_date')[:5]
        
        context = {
            'lecturer': lecturer,
            'department': department,
            'unit_allocations': current_courses,  # Changed from 'courses' to 'unit_allocations'
            'schedule': today_schedule,
            'today_weekday': today_weekday,  # For debugging
            'tasks': pending_tasks,
            'announcements': announcements,
            'current_semester': current_semester,
            'current_year': current_year,
            'page_title': 'Lecturer Dashboard',
        }
        
        return render(request, 'dashboards/lecturer_dashboard.html', context)
    
    except Lecturer.DoesNotExist:
        messages.error(request, "Lecturer profile not found. Please contact administration.")
        return redirect('login')


@require_GET
def gender_distribution_api(request):
    academic_year_id = request.GET.get('academic_year')
    try:
        academic_year_id = int(academic_year_id)
        gender_data = prepare_gender_data_by_academic_year(academic_year_id)
        return JsonResponse(gender_data, safe=False)
    except (ValueError, AcademicYear.DoesNotExist):
        return JsonResponse({'error': 'Invalid academic year'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def prepare_gender_data_by_academic_year(academic_year_id):
    academic_year = AcademicYear.objects.get(id=academic_year_id)
    
    # Get students admitted during this academic year
    students = Student.objects.filter(
        date_of_admission__gte=academic_year.start_date,
        date_of_admission__lte=academic_year.end_date
    )
    
    # Count by gender
    gender_counts = {
        'M': students.filter(gender='M').count(),
        'F': students.filter(gender='F').count(),
        'O': students.filter(gender='O').count()
    }
    
    return [
        {'value': gender_counts['M'], 'name': 'Male'},
        {'value': gender_counts['F'], 'name': 'Female'},
        {'value': gender_counts['O'], 'name': 'Other'}
    ]


@login_required
def admin_dashboard(request):
    # Get all academic years ordered chronologically
    academic_years = AcademicYear.objects.order_by('start_date')
    
    # Prepare data for the bar chart
    academic_year_labels = []
    academic_year_data = []
    
    for academic_year in academic_years:
        # Count students admitted during this academic year period
        count = Student.objects.filter(
            date_of_admission__gte=academic_year.start_date,
            date_of_admission__lte=academic_year.end_date
        ).count()
        
        academic_year_labels.append(academic_year.name)
        academic_year_data.append(count)

    # Student statistics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='active').count()
    
    # Lecturer statistics
    total_lecturers = Lecturer.objects.count()
    active_lecturers = Lecturer.objects.filter(status='active').count()
    
    # Programme statistics
    total_programmes = Programme.objects.count()
    total_departments = Department.objects.count()
    total_faculties = Faculty.objects.count()
    
    # Latest students and lecturers
    latest_students = Student.objects.order_by('-created_at')[:8]
    latest_lecturers = Lecturer.objects.order_by('-created_at')[:8]
    
    # Get academic years from AcademicYear model
    academic_years = AcademicYear.objects.order_by('-start_date')
    academic_year_choices = [(year.id, f"{year.name} ({year.start_date.year})") for year in academic_years]
    
    # Get current academic year
    current_academic_year = AcademicYear.objects.filter(is_current=True).first()
    if not current_academic_year:
        current_academic_year = academic_years.first()
    
    # Prepare gender data for current academic year
    gender_data = prepare_gender_data_by_academic_year(current_academic_year.id) if current_academic_year else []
    
    # Prepare student population trend data
    current_year = datetime.now().year
    year_range = range(current_year - 4, current_year + 1)
    population_trend_labels = list(year_range)
    population_trend_data = []
    
    for year in year_range:
        count = Student.objects.filter(
            date_of_admission__year__lte=year
        ).count()
        population_trend_data.append(count)
    
    # Prepare reporting statistics
    # Group reporting statistics by academic year and semester
    reporting_trend_data = defaultdict(lambda: {'reported': 0, 'not_reported': 0, 'deferred': 0})

    # Get all reportings and group
    all_reportings = StudentReporting.objects.select_related('academic_year', 'semester')
    for report in all_reportings:
        label = f"{report.academic_year.name} - {report.semester.name}"  # E.g., "2023/2024 - Semester 1"
        reporting_trend_data[label][report.reporting_status] += 1

    # Sort by academic year and semester
    sorted_labels = sorted(reporting_trend_data.keys())
    reported_data = [reporting_trend_data[label]['reported'] for label in sorted_labels]
    not_reported_data = [reporting_trend_data[label]['not_reported'] for label in sorted_labels]
    deferred_data = [reporting_trend_data[label]['deferred'] for label in sorted_labels]
    
    context = {
        'page_title': 'Admin Dashboard',
        'active_tab': 'dashboard',
        'user': request.user,
        
        # Statistics
        'total_students': total_students,
        'active_students': active_students,
        'total_lecturers': total_lecturers,
        'active_lecturers': active_lecturers,
        'total_programmes': total_programmes,
        'total_departments': total_departments,
        'total_faculties': total_faculties,
        
        # Latest records
        'latest_students': latest_students,
        'latest_lecturers': latest_lecturers,
        
        # Chart data
        'academic_year_labels': json.dumps(academic_year_labels),
        'academic_year_data': json.dumps(academic_year_data),
        'population_trend_labels': json.dumps(population_trend_labels),
        'population_trend_data': json.dumps(population_trend_data),
        'gender_data': json.dumps(gender_data),
        #reportings
        'reporting_labels': json.dumps(sorted_labels),
        'reported_data': json.dumps(reported_data),
        'not_reported_data': json.dumps(not_reported_data),
        'deferred_data': json.dumps(deferred_data),

        
        # Academic year filter
        'academic_year_choices': academic_year_choices,
        'current_academic_year': current_academic_year.id if current_academic_year else None,
        'current_academic_year_display': current_academic_year.name if current_academic_year else "N/A",
    }
    
    return render(request, 'dashboards/admin_dashboard.html', context)


@login_required
def staff_dashboard(request):
    context = {
        'page_title': 'Staff Dashboard',
        'active_tab': 'dashboard',
        'user': request.user
    }
    return render(request, 'dashboards/staff_dashboard.html', context)

@login_required
def finance_dashboard(request):
    context = {
        'page_title': 'Finance Dashboard',
        'active_tab': 'dashboard',
        'user': request.user
    }
    return render(request, 'dashboards/finance_dashboard.html', context)




@login_required
def database_students_list(request):
    students = Student.objects.all()
    return render(request, 'students/database_student_list.html', {'students': students})


@login_required

def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "student record created successfully.")
            return redirect('database_students_list')
    else:
        form = StudentForm()
    return render(request, 'students/student_form.html', {'form': form})


@login_required

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'students/student_detail.html', {'student': student})


@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"Student {student.first_name} {student.last_name} has been successfully updated.")
            return redirect('database_students_list')
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'students/student_form.html', {'form': form})



@login_required

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})



def lecturer_list(request):
    """List all lecturers"""
    lecturers = Lecturer.objects.all().order_by('last_name')
    context = {
        'lecturers': lecturers,
        'title': 'Lecturer List'
    }
    return render(request, 'lecturers/lecturer_list.html', context)

def lecturer_detail(request, pk):
    """View details of a specific lecturer"""
    lecturer = get_object_or_404(Lecturer, pk=pk)
    context = {
        'lecturer': lecturer,
        'title': f'Lecturer Details - {lecturer.get_full_name()}'
    }
    return render(request, 'lecturers/lecturer_detail.html', context)

def lecturer_create(request):
    """Create a new lecturer"""
    if request.method == 'POST':
        form = LecturerForm(request.POST, request.FILES)
        if form.is_valid():
            lecturer = form.save()
            return redirect('lecturer_detail', pk=lecturer.pk)
    else:
        form = LecturerForm()
    
    context = {
        'form': form,
        'title': 'Add New Lecturer'
    }
    return render(request, 'lecturers/lecturer_form.html', context)

def lecturer_update(request, pk):
    """Update an existing lecturer"""
    lecturer = get_object_or_404(Lecturer, pk=pk)
    
    if request.method == 'POST':
        form = LecturerForm(request.POST, request.FILES, instance=lecturer)
        if form.is_valid():
            form.save()
            return redirect('lecturer_detail', pk=lecturer.pk)
    else:
        form = LecturerForm(instance=lecturer)
    
    context = {
        'form': form,
        'lecturer': lecturer,
        'title': f'Update Lecturer - {lecturer.get_full_name()}'
    }
    return render(request, 'lecturers/lecturer_form.html', context)

def lecturer_delete(request, pk):
    """Delete a lecturer"""
    lecturer = get_object_or_404(Lecturer, pk=pk)
    
    if request.method == 'POST':
        lecturer.delete()
        return redirect('lecturer_list')
    
    context = {
        'lecturer': lecturer,
        'title': f'Delete Lecturer - {lecturer.get_full_name()}'
    }
    return render(request, 'lecturers/lecturer_confirm_delete.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import (
    Student, ProgrammeUnit, StudentEnrollment, 
    Semester, AcademicYear, UnitAllocation
)

@login_required
def unit_enrollment(request):
    try:
        # Get student directly using the username (which is admission number)
        student = Student.objects.get(registration_number=request.user.username)
    except Student.DoesNotExist:
        messages.error(request, "Student record not found")
        return redirect('student_dashboard')
    
    current_semester = Semester.objects.filter(is_current=True).first()
    
    if not current_semester:
        messages.error(request, "No active semester found for enrollment")
        return redirect('student_dashboard')
    
    # Get all units available for the student's programme, year and semester
    available_units = ProgrammeUnit.objects.filter(
        programme=student.programme,
        year_of_study=student.current_year,
        semester=student.current_semester
    ).select_related('unit')
    
    # Get units the student is already enrolled in for this semester
    enrolled_units = StudentEnrollment.objects.filter(
        student=student,
        semester=current_semester
    ).values_list('programme_unit_id', flat=True)
    
    # Get current enrollments to display in the template
    current_enrollments = StudentEnrollment.objects.filter(
        student=student,
        semester=current_semester
    ).select_related('programme_unit__unit')
    
    if request.method == 'POST':
        # Handle form submission
        selected_units = request.POST.getlist('units')
        
        # Validate selected units
        valid_units = available_units.filter(id__in=selected_units)
        
        # Check for already enrolled units
        new_units = valid_units.exclude(id__in=enrolled_units)
        
        # Create enrollments
        enrollments_created = 0
        for unit in new_units:
            StudentEnrollment.objects.create(
                student=student,
                programme_unit=unit,
                semester=current_semester
            )
            enrollments_created += 1
        
        if enrollments_created > 0:
            messages.success(request, f"Successfully enrolled in {enrollments_created} units")
        else:
            messages.warning(request, "No new units were enrolled")
        
        return redirect('unit_enrollment')
    
    context = {
        'student': student,
        'available_units': available_units,
        'enrolled_units': enrolled_units,
        'current_semester': current_semester,
        'current_enrollments': current_enrollments,  # Add this to context
        'max_units': 6,  # You can set a maximum number of units per semester
    }
    
    return render(request, 'enrollment/unit_enrollment.html', context)


@login_required
def drop_unit(request, enrollment_id):
    try:
        # Get student directly using the username (which is admission number)
        student = Student.objects.get(registration_number=request.user.username)
    except Student.DoesNotExist:
        messages.error(request, "Student record not found")
        return redirect('student_dashboard')
    
    enrollment = get_object_or_404(StudentEnrollment, id=enrollment_id, student=student)
    
    # Check if it's allowed to drop this unit (you might want to add deadline checks)
    current_semester = Semester.objects.filter(is_current=True).first()
    
    if enrollment.semester != current_semester:
        messages.error(request, "You can only drop units from the current semester")
        return redirect('unit_enrollment')
    
    enrollment.delete()
    messages.success(request, f"You have successfully dropped {enrollment.programme_unit.unit.name}")
    
    return redirect('unit_enrollment')


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import StudentReporting, Semester, Student

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import StudentReporting, Semester, Student

@login_required
def report_for_semester(request):
    """
    View for students to report for the current active semester
    using username (admission number) for authentication
    """
    try:
        # Get student directly using the username (which is admission number)
        student = Student.objects.get(registration_number=request.user.username)
    except Student.DoesNotExist:
        messages.error(request, "Student record not found")
        return redirect('student_dashboard')

    # Get current active semester
    current_semester = Semester.objects.filter(is_current=True).first()
    
    if not current_semester:
        messages.error(request, "No active semester found for reporting.")
        return redirect('student_dashboard')

    # Check if already reported
    existing_report = StudentReporting.objects.filter(
        student=student,
        academic_year=current_semester.academic_year,
        semester=current_semester
    ).first()


    # Fetch all past reportings for this student
    past_reportings = StudentReporting.objects.filter(
        student=student
    ).order_by('-reporting_date')

    if request.method == 'POST':
        # Handle form submission
        if existing_report:
            messages.warning(request, "You have already reported for this semester.")
        else:
            # Create new reporting record
            StudentReporting.objects.create(
                student=student,
                academic_year=current_semester.academic_year,
                programme=student.programme,
                semester=current_semester,
                reporting_status='reported',
                reporting_date=timezone.now().date(),
                is_fees_cleared=request.POST.get('fees_cleared') == 'on',
                notes=request.POST.get('notes', '')
            )
            messages.success(request, "Successfully reported for the semester!")
        return redirect('student_dashboard')

    context = {
        'student': student,
        'current_semester': current_semester,
        'already_reported': existing_report is not None,
        'reporting_record': existing_report,
        'past_reportings': past_reportings,
    }
    return render(request, 'students/report_for_semester.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch, Q

from .models import (
    Student, 
    StudentEnrollment, 
    StudentUnitGrade, 
    AcademicYear, 
    Semester
)

"""
Displays academic results for logged-in students, fetching only years since admission date.
Organizes results hierarchically by academic years and semesters with detailed unit grades.
Shows complete grade information when available or marks courses as "Pending" when grades aren't finalized.
"""

@login_required
def student_results_view(request):
    """
    View for students to see their academic results by year and semester.
    """
    # Get the student profile associated with the logged-in user
    try:
        student = Student.objects.get(
            registration_number=request.user.username
        )
    except Student.DoesNotExist:
        messages.error(request, "No student profile found for your account.")
        return render(request, 'students/no_profile.html')

    # **Fetch only academic years where the student has enrollments**
    enrolled_semester_ids = StudentEnrollment.objects.filter(
        student=student
    ).values_list('semester_id', flat=True).distinct()
    
    # Get academic years that contain these semesters
    academic_years = AcademicYear.objects.filter(
        semesters__id__in=enrolled_semester_ids
    ).distinct().order_by('-start_date')
    # Initialize data structure to hold results
    results_by_year = {}

    for academic_year in academic_years:
        # Get semesters for this academic year
        semesters = Semester.objects.filter(
            academic_year=academic_year
        ).order_by('number')

        # Initialize semester results
        semester_results = {}

        for semester in semesters:
            # Get enrollments for this student in this semester
            enrollments = StudentEnrollment.objects.filter(
                student=student,
                semester=semester
            ).select_related(
                'programme_unit__unit'
            ).prefetch_related(
                Prefetch(
                    'final_grade',
                    queryset=StudentUnitGrade.objects.select_related('grade')
                )
            )

            # Process and structure the results data
            units_results = []

            for enrollment in enrollments:
                unit = enrollment.programme_unit.unit

                # Try to get the grade for this enrollment
                if hasattr(enrollment, 'final_grade'):
                    grade = enrollment.final_grade
                    unit_result = {
                        'unit_code': unit.code,
                        'unit_name': unit.name,
                        'credit_hours': unit.credit_hours,
                        'cat_score': grade.cat_average,
                        'exam_score': grade.exam_score,
                        'total_score': grade.total_score,
                        'grade': grade.grade.grade,
                        'points': grade.grade.points,
                        'is_pass': grade.is_pass,
                        'remarks': grade.remarks,
                    }
                else:
                    unit_result = {
                        'unit_code': unit.code,
                        'unit_name': unit.name,
                        'credit_hours': unit.credit_hours,
                        'status': 'Pending',
                    }

                units_results.append(unit_result)

            # Add results to semester
            semester_results[semester.number] = {
                'semester_name': semester.name,
                'units': units_results,
            }

        # Add semester results to the academic year
        results_by_year[academic_year.name] = {
            'semesters': semester_results,
            'year_name': academic_year.name,
        }

    context = {
        'student': student,
        'results_by_year': results_by_year,
    }

    return render(request, 'students/academic_results.html', context)


from django.http import HttpResponse
from django.conf import settings
from .utils import render_to_pdf
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os

from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from datetime import datetime
import os
from django.conf import settings

from .models import Student, AcademicYear, Semester, StudentEnrollment, StudentUnitGrade
from .utils import render_to_pdf

from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from datetime import datetime
import os
from django.conf import settings

from .models import Student, AcademicYear, Semester, StudentEnrollment, StudentUnitGrade

from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from datetime import datetime
import os
from django.conf import settings

from .models import Student, AcademicYear, Semester, StudentEnrollment, StudentUnitGrade
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)


@login_required
def download_transcript(request):
    """
    View to download student transcript as PDF with improved error handling
    """
    # Get the student profile
    try:
        student = Student.objects.get(registration_number=request.user.username)
    except Student.DoesNotExist:
        messages.error(request, "No student profile found for your account.")
        return HttpResponse("No student profile found", status=404)

    try:
        # Get academic results
        academic_years = AcademicYear.objects.filter(
            start_date__gte=student.date_of_admission,
            semesters__id__isnull=False
        ).distinct().order_by('-start_date')

        results_by_year = {}
        total_credit_hours = 0
        total_grade_points = 0

        # Process academic data
        for academic_year in academic_years:
            semesters = Semester.objects.filter(academic_year=academic_year).order_by('number')
            semester_results = {}

            for semester in semesters:
                enrollments = StudentEnrollment.objects.filter(
                    student=student,
                    semester=semester
                ).select_related(
                    'programme_unit__unit', 
                    'final_grade__grade'
                )

                units_results = []
                semester_credit_hours = 0
                semester_grade_points = 0

                for enrollment in enrollments:
                    unit = enrollment.programme_unit.unit
                    
                    if hasattr(enrollment, 'final_grade') and enrollment.final_grade:
                        grade = enrollment.final_grade
                        unit_result = {
                            'unit_code': unit.code,
                            'unit_name': unit.name,
                            'credit_hours': unit.credit_hours,
                            'cat_score': getattr(grade, 'cat_average', 0),
                            'exam_score': getattr(grade, 'exam_score', 0),
                            'total_score': getattr(grade, 'total_score', 0),
                            'grade': getattr(grade.grade, 'grade', 'N/A'),
                            'points': getattr(grade.grade, 'points', 0),
                            'is_pass': getattr(grade, 'is_pass', False),
                            'remarks': getattr(grade, 'remarks', ''),
                        }
                        
                        if unit_result['is_pass']:
                            semester_credit_hours += unit.credit_hours
                            semester_grade_points += (unit.credit_hours * unit_result['points'])
                    else:
                        unit_result = {
                            'unit_code': unit.code,
                            'unit_name': unit.name,
                            'credit_hours': unit.credit_hours,
                            'status': 'Pending',
                        }

                    units_results.append(unit_result)

                # Calculate semester GPA
                semester_gpa = round(semester_grade_points / semester_credit_hours, 2) if semester_credit_hours > 0 else 0

                semester_results[semester.number] = {
                    'semester_name': semester.name,
                    'units': units_results,
                    'semester_credit_hours': semester_credit_hours,
                    'semester_grade_points': semester_grade_points,
                    'semester_gpa': semester_gpa
                }

                total_credit_hours += semester_credit_hours
                total_grade_points += semester_grade_points

            results_by_year[academic_year.name] = {
                'semesters': semester_results,
                'year_name': academic_year.name,
            }

        # Calculate cumulative GPA
        cumulative_gpa = round(total_grade_points / total_credit_hours, 2) if total_credit_hours > 0 else 0
        
        # Prepare context with absolute URLs
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        
        context = {
            'student': student,
            'results_by_year': results_by_year,
            'total_credit_hours': total_credit_hours,
            'cumulative_gpa': cumulative_gpa,
            'today': datetime.now(),
            'university_name': getattr(settings, 'UNIVERSITY_NAME', 'University'),
            'school_logo': f"{protocol}://{host}{settings.MEDIA_URL}school_logo.png",
            'official_stamp': f"{protocol}://{host}{settings.MEDIA_URL}official_stamp.png",
            'debug': settings.DEBUG,  # Useful for template conditional debugging
        }

        # Generate PDF
        pdf_content = render_to_pdf('students/transcript_template.html', context)
        
        if not pdf_content:
            messages.error(request, "Failed to generate PDF transcript")
            return HttpResponse("Failed to generate PDF", status=500)
            
        # Create response
        filename = f"Transcript_{student.registration_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"Error generating transcript: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while generating your transcript")
        return HttpResponse(f"Error generating transcript: {str(e)}", status=500)


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Student, StudentEnrollment, StudentUnitGrade, GradeSystem, AcademicYear, Semester
import json

def search_student(request):
    """Search for a student by registration number and return enrolled units with existing grades"""
    registration_number = request.GET.get('registration_number')

    try:
        student = get_object_or_404(Student, registration_number=registration_number)
        current_semester = Semester.objects.filter(is_current=True).first()

        if not current_semester:
            return JsonResponse({'error': 'No active semester found'}, status=400)

        enrollments = StudentEnrollment.objects.filter(
            student=student,
            semester=current_semester
        ).select_related('programme_unit__unit', 'semester__academic_year')

        units = []
        for enrollment in enrollments:
            # Check if there's an existing grade record for this enrollment
            grade = StudentUnitGrade.objects.filter(enrollment=enrollment).first()
            
            unit_data = {
                'enrollment_id': enrollment.id,
                'unit_code': enrollment.programme_unit.unit.code,
                'unit_name': enrollment.programme_unit.unit.name,
                'cat_score': grade.cat_average if grade else None,
                'exam_score': grade.exam_score if grade else None,
                'total_score': grade.total_score if grade else None,
                'grade': grade.grade.grade if grade and grade.grade else None,
                'is_pass': grade.is_pass if grade else None
            }
            units.append(unit_data)

        return JsonResponse({
            'student_name': student.get_full_name(),
            'registration_number': student.registration_number,
            'academic_year': current_semester.academic_year.name,
            'semester': current_semester.name,
            'units': units
        }, status=200)

    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)


def enter_student_grades(request):
    """Render the form for entering student grades and allow searching by student registration number"""
    
    students = Student.objects.all()  # Get all students for dropdown search

    context = {
        'students': students
    }
    return render(request, 'students/enter_grades.html', context)


from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json

@require_POST
def save_student_grades(request):
    try:
        # Ensure request is AJAX/JSON
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid request'}, status=400)
            
        data = json.loads(request.body)
        student_reg = data.get('registration_number')
        grades = data.get('grades', [])

        if not student_reg:
            return JsonResponse({'error': 'Registration number required'}, status=400)

        student = get_object_or_404(Student, registration_number=student_reg)
        
        results = []
        for grade_data in grades:
            try:
                enrollment = StudentEnrollment.objects.get(
                    id=grade_data['enrollment_id'],
                    student=student
                )
                
                cat_score = float(grade_data.get('cat_score', 0))
                exam_score = float(grade_data.get('exam_score', 0))
                total_score = cat_score + exam_score

                grade = GradeSystem.objects.filter(
                    min_score__lte=total_score,
                    max_score__gte=total_score
                ).first()
                
                obj, created = StudentUnitGrade.objects.update_or_create(
                    enrollment=enrollment,
                    defaults={
                        'cat_average': cat_score,
                        'exam_score': exam_score,
                        'total_score': total_score,
                        'grade': grade,
                        'is_pass': total_score >= 50
                    }
                )
                
                results.append({
                    'enrollment_id': enrollment.id,
                    'status': 'success',
                    'grade': grade.grade if grade else None
                })
                
            except Exception as e:
                results.append({
                    'enrollment_id': grade_data.get('enrollment_id'),
                    'status': 'error',
                    'message': str(e)
                })

        return JsonResponse({
            'message': 'Grades processed',
            'results': results
        }, status=200)

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)




from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Student
from .forms import StudentSearchForm

@login_required
def search_student_data(request):
    """View for searching students with various filter criteria"""
    form = StudentSearchForm(request.GET or None)
    students = None
    
    if request.GET:
        # Form was submitted, apply filters
        students = Student.objects.all()
        
        # Apply filters based on form data
        if request.GET.get('registration_number'):
            students = students.filter(registration_number__icontains=request.GET.get('registration_number'))
        
        if request.GET.get('name'):
            name_query = request.GET.get('name')
            name_filter = Q(first_name__icontains=name_query) | \
                          Q(last_name__icontains=name_query) | \
                          Q(middle_name__icontains=name_query)
            students = students.filter(name_filter)
        
        if request.GET.get('programme') and request.GET.get('programme') != '':
            students = students.filter(programme_id=request.GET.get('programme'))
        
        if request.GET.get('current_year') and request.GET.get('current_year') != '0':
            students = students.filter(current_year=request.GET.get('current_year'))
        
        if request.GET.get('status') and request.GET.get('status') != '':
            students = students.filter(status=request.GET.get('status'))
        
        if request.GET.get('entry_mode') and request.GET.get('entry_mode') != '':
            students = students.filter(entry_mode=request.GET.get('entry_mode'))
        
        if request.GET.get('email'):
            students = students.filter(email__icontains=request.GET.get('email'))
        
        if request.GET.get('phone_number'):
            students = students.filter(phone_number__icontains=request.GET.get('phone_number'))
        
        if request.GET.get('id_number'):
            students = students.filter(id_number__icontains=request.GET.get('id_number'))
        
        # Order results
        students = students.order_by('registration_number')
    
    context = {
        'form': form,
        'students': students
    }
    
    return render(request, 'students/search_student.html', context)

from django.db.models import Avg, Sum, Count
from collections import defaultdict

def get_student_academic_progress(student):
    """
    Get complete academic progress for a student using existing models
    Returns a structured dictionary with all academic years and semesters
    Handles enrollments that may not have final grades yet
    """
    # Get all enrollments for the student ordered by semester
    enrollments = StudentEnrollment.objects.filter(
        student=student
    ).select_related(
        'semester__academic_year',
        'programme_unit__unit',
        'programme_unit__programme'
    ).prefetch_related(
        'final_grade',
        'final_grade__grade'
    ).order_by('semester__academic_year__start_date', 'semester__number')
    
    # Organize data by academic year and semester
    progress_data = {
        'student': {
            'name': student.get_full_name(),
            'reg_number': student.registration_number,
            'programme': student.programme.name,
            'admission_date': student.date_of_admission,
            'current_year': student.current_year,
            'current_semester': student.current_semester
        },
        'academic_years': defaultdict(lambda: {
            'name': None,
            'start_date': None,
            'end_date': None,
            'semesters': defaultdict(lambda: {
                'name': None,
                'number': None,
                'start_date': None,
                'end_date': None,
                'units': [],
                'summary': {
                    'total_credits': 0,
                    'earned_credits': 0,
                    'gpa': 0.0,
                    'units_attempted': 0,
                    'units_passed': 0
                }
            })
        })
    }
    
    # Process each enrollment to build the progress structure
    for enrollment in enrollments:
        academic_year = enrollment.semester.academic_year
        semester = enrollment.semester
        programme_unit = enrollment.programme_unit
        unit = programme_unit.unit
        
        # Safely get final_grade - handle the case when it doesn't exist
        try:
            final_grade = enrollment.final_grade
            has_final_grade = True
        except:
            final_grade = None
            has_final_grade = False
        
        # Set academic year info if not already set
        if not progress_data['academic_years'][academic_year.id]['name']:
            progress_data['academic_years'][academic_year.id]['name'] = academic_year.name
            progress_data['academic_years'][academic_year.id]['start_date'] = academic_year.start_date
            progress_data['academic_years'][academic_year.id]['end_date'] = academic_year.end_date
        
        # Set semester info if not already set
        if not progress_data['academic_years'][academic_year.id]['semesters'][semester.number]['name']:
            progress_data['academic_years'][academic_year.id]['semesters'][semester.number]['name'] = semester.name
            progress_data['academic_years'][academic_year.id]['semesters'][semester.number]['number'] = semester.number
            progress_data['academic_years'][academic_year.id]['semesters'][semester.number]['start_date'] = semester.start_date
            progress_data['academic_years'][academic_year.id]['semesters'][semester.number]['end_date'] = semester.end_date
        
        # Add unit information - safely handle final_grade references
        unit_data = {
            'code': unit.code,
            'name': unit.name,
            'credit_hours': unit.credit_hours,
            'is_core': unit.is_core,
            'year_of_study': programme_unit.year_of_study,
            'semester': programme_unit.semester,
            'cat_average': final_grade.cat_average if has_final_grade else None,
            'exam_score': final_grade.exam_score if has_final_grade else None,
            'total_score': final_grade.total_score if has_final_grade else None,
            'grade': final_grade.grade.grade if has_final_grade and final_grade.grade else None,
            'is_pass': final_grade.is_pass if has_final_grade else None,
            'graded': has_final_grade  # Flag to indicate if unit has been graded
        }
        
        progress_data['academic_years'][academic_year.id]['semesters'][semester.number]['units'].append(unit_data)
        
        # Update semester summary - only count units with final grades
        if has_final_grade:
            progress_data['academic_years'][academic_year.id]['semesters'][semester.number]['summary']['total_credits'] += unit.credit_hours
            progress_data['academic_years'][academic_year.id]['semesters'][semester.number]['summary']['units_attempted'] += 1
            
            if final_grade.is_pass:
                progress_data['academic_years'][academic_year.id]['semesters'][semester.number]['summary']['earned_credits'] += unit.credit_hours
                progress_data['academic_years'][academic_year.id]['semesters'][semester.number]['summary']['units_passed'] += 1
    
    # Calculate GPA for each semester
    for year_data in progress_data['academic_years'].values():
        for semester_data in year_data['semesters'].values():
            total_quality_points = 0
            total_credits = 0
            
            for unit in semester_data['units']:
                if unit.get('grade') and unit.get('is_pass'):
                    # Get grade points from GradeSystem
                    try:
                        grade = GradeSystem.objects.get(grade=unit['grade'])
                        total_quality_points += grade.points * unit['credit_hours']
                        total_credits += unit['credit_hours']
                    except GradeSystem.DoesNotExist:
                        pass
            
            if total_credits > 0:
                semester_data['summary']['gpa'] = round(total_quality_points / total_credits, 2)
    
    # Convert defaultdict to regular dict for JSON serialization
    progress_data['academic_years'] = {
        year_id: {
            **year_data,
            'semesters': dict(sorted(year_data['semesters'].items()))
        }
        for year_id, year_data in sorted(progress_data['academic_years'].items())
    }
    
    return progress_data

def get_student_transcript(student):
    """
    Generate a formal transcript using existing models
    """
    progress_data = get_student_academic_progress(student)
    
    # Calculate cumulative GPA and credits
    total_quality_points = 0
    total_credits = 0
    cumulative_credits = 0
    
    for year_data in progress_data['academic_years'].values():
        for semester_data in year_data['semesters'].values():
            semester_credits = semester_data['summary']['earned_credits']
            semester_gpa = semester_data['summary']['gpa']
            
            if semester_credits > 0:
                total_quality_points += semester_gpa * semester_credits
                total_credits += semester_credits
                cumulative_credits += semester_credits
    
    cumulative_gpa = round(total_quality_points / total_credits, 2) if total_credits > 0 else 0.0
    
    transcript = {
        'student_info': progress_data['student'],
        'academic_years': progress_data['academic_years'],
        'cumulative_summary': {
            'gpa': cumulative_gpa,
            'total_credits': cumulative_credits
        }
    }
    
    return transcript


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

def student_progress_report(request, student_id):
    """View to display student progress report"""
    student = get_object_or_404(Student, pk=student_id)
    
    # Check permissions here (e.g., only student or admin can view)
    
    progress_data = get_student_academic_progress(student)
    
    context = {
        'student': student,
        'progress_data': progress_data
    }
    
    return render(request, 'academics/student_progress.html', context)

def student_official_transcript(request, student_id):
    """View to generate official transcript"""
    student = get_object_or_404(Student, pk=student_id)
    
    # Check permissions here
    
    transcript = get_student_transcript(student)
    
    context = {
        'student': student,
        'transcript': transcript
    }
    
    return render(request, 'academics/official_transcript.html', context)

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

def api_student_progress(request, student_id):
    """View for student progress with academic year tabs and semester breakdown"""
    student = get_object_or_404(Student, pk=student_id)
    
    # Check permissions here if needed
    
    progress_data = get_student_academic_progress(student)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If AJAX request, return JSON
        return JsonResponse(progress_data)
    
    # For regular browser requests, return HTML
    return render(request, 'academics/student_progress_tabs.html', {
        'student': student,
        'progress_data': progress_data
    })



def programme_list(request):
    programmes = Programme.objects.all().select_related('department')
    return render(request, 'academics/programme_list.html', {'programmes': programmes})

def programme_detail(request, programme_id):
    programme = get_object_or_404(Programme, id=programme_id)
    programme_units = ProgrammeUnit.objects.filter(programme=programme).select_related('unit')
    
    # Get unique years and semesters for this programme
    years = sorted(set(pu.year_of_study for pu in programme_units))
    semesters = sorted(set(pu.semester for pu in programme_units))
    
    context = {
        'programme': programme,
        'programme_units': programme_units,
        'years': years,
        'semesters': semesters,
    }
    return render(request, 'academics/programme_detail.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count
from .models import Student, StudentUnitGrade, StudentFee, Programme, FeesStructure, AcademicYear, Semester
from datetime import date

@login_required
@user_passes_test(lambda u: u.is_staff)
def promote_students(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                promoted_students = []
                not_promoted_students = []
                graduated_students = []
                
                # Get current academic year and semester
                current_academic_year = AcademicYear.objects.filter(is_current=True).first()
                current_semester = Semester.objects.filter(is_current=True).first()
                
                if not current_academic_year or not current_semester:
                    messages.error(request, "Current academic year or semester not set in system")
                    return redirect('promote_students')
                
                active_students = Student.objects.filter(status='active').select_related('programme')
                
                for student in active_students:
                    programme = student.programme
                    current_year = student.current_year
                    current_semester = student.current_semester
                    
                    failed_units = StudentUnitGrade.objects.filter(
                        enrollment__student=student,
                        is_pass=False
                    ).count()
                    
                    has_balance = StudentFee.objects.filter(
                        student=student,
                        balance__gt=0
                    ).exists()
                    
                    student_data = {
                        'id': student.id,
                        'name': f"{student.first_name} {student.last_name}",
                        'reg_no': student.registration_number,
                        'programme': programme.name,
                        'current_year': current_year,
                        'current_semester': current_semester,
                    }
                    
                    if failed_units <= 3 and not has_balance:
                        if current_year == programme.duration_years and current_semester == programme.semesters_per_year:
                            # Graduation logic
                            student.status = 'graduated'
                            student.is_active = False
                            student.save()
                            
                            graduated_students.append({
                                **student_data,
                                'completion': f"Year {current_year} Semester {current_semester}"
                            })
                        else:
                            # Promotion logic
                            new_year = current_year
                            new_semester = current_semester + 1
                            
                            if new_semester > programme.semesters_per_year:
                                new_year += 1
                                new_semester = 1
                            
                            student.current_year = new_year
                            student.current_semester = new_semester
                            student.save()
                            
                            # Create fee record for the new semester
                            try:
                                fee_structure = FeesStructure.objects.get(
                                    programme=programme,
                                    academic_year=current_academic_year,
                                    year_of_study=new_year,
                                    semester=new_semester
                                )
                                
                                StudentFee.objects.create(
                                    student=student,
                                    fee_structure=fee_structure,
                                    amount_paid=0,
                                    balance=fee_structure.amount,
                                    last_payment_date=None
                                )
                                
                                fee_created = True
                            except FeesStructure.DoesNotExist:
                                fee_created = False
                            
                            promoted_students.append({
                                **student_data,
                                'new_year': new_year,
                                'new_semester': new_semester,
                                'fee_created': fee_created
                            })
                    else:
                        # Not promoted logic
                        reasons = []
                        if failed_units > 3:
                            reasons.append(f"Failed {failed_units} units")
                        if has_balance:
                            reasons.append("Outstanding balance")
                            
                        not_promoted_students.append({
                            **student_data,
                            'reason': ", ".join(reasons)
                        })
                
                promoted_by_programme = {}
                for student in promoted_students:
                    programme_name = student['programme']
                    if programme_name not in promoted_by_programme:
                        promoted_by_programme[programme_name] = {
                            'students': [],
                            'from': f"Y{student['current_year']}S{student['current_semester']}",
                            'to': f"Y{student['new_year']}S{student['new_semester']}",
                            'fee_status': "Created" if student['fee_created'] else "Not created (no fee structure)"
                        }
                    promoted_by_programme[programme_name]['students'].append(student)
                
                context = {
                    'promoted_by_programme': promoted_by_programme,
                    'graduated_students': graduated_students,
                    'not_promoted_students': not_promoted_students,
                    'total_promoted': len(promoted_students),
                    'total_graduated': len(graduated_students),
                    'total_not_promoted': len(not_promoted_students),
                    'current_academic_year': current_academic_year.name,
                }
                
                return render(request, 'students/promote_students.html', context)
                
        except Exception as e:
            messages.error(request, f"Error during promotion: {str(e)}")
            return redirect('promote_students')
    
    # GET request - show empty form
    return render(request, 'students/promote_students.html')

@login_required
def student_profile_view(request):
    """
    View function to handle student profile display and updates.
    Uses a dedicated form for profile updates only.
    """
    try:
        # Get student directly using the username (which is admission number)
        student = Student.objects.get(registration_number=request.user.username)
        
        if request.method == 'POST':
            # Use the dedicated profile update form
            form = StudentProfileUpdateForm(
                request.POST, 
                request.FILES, 
                instance=student
            )
            
            # Handle profile image removal
            if 'remove_profile_image' in request.POST:
                if student.profile_picture:
                    # Store the path to delete after saving
                    old_image = student.profile_picture.path if student.profile_picture else None
                    student.profile_picture = None  # Clear the field
                    student.save()  # Save the change
                    
                    # Delete the actual file if it exists
                    if old_image and os.path.isfile(old_image):
                        import os
                        os.remove(old_image)
                        
                    messages.success(request, 'Profile picture removed successfully')
                else:
                    messages.info(request, 'No profile picture to remove')
                return redirect('student_profile')
            
            if form.is_valid():
                # Save the form and get the instance
                updated_student = form.save(commit=True)
                
                # Check which fields were actually changed
                changed_fields = []
                for field in form.changed_data:
                    if field != 'profile_picture':  # Skip the image field in this check
                        changed_fields.append(field)
                
                if changed_fields:
                    messages.success(request, f'Profile updated successfully. Changed fields: {", ".join(changed_fields)}')
                elif 'profile_picture' in form.changed_data:
                    messages.success(request, 'Profile picture updated successfully')
                else:
                    messages.info(request, 'No changes were made to your profile')
                
                return redirect('student_profile')
                
            else:
                # Show specific field errors and print them for debugging
                print(f"Form errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field.replace("_", " ").title()}: {error}')
        else:
            # Just display the form - not posting
            form = StudentProfileUpdateForm(instance=student)
            
        context = {
            'student': student,
            'form': form
        }
        return render(request, 'students/profile.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, "Student record not found. Please contact administration.")
        return redirect('student_dashboard')
    except Exception as e:
        # Catch other errors and provide helpful debugging
        messages.error(request, f"An error occurred: {str(e)}")
        print(f"Error in student_profile_view: {str(e)}")
        return redirect('student_dashboard')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from .models import Student, StudentFee, FeePayment, FeesStructure, AcademicYear, Semester

@login_required
def student_fee_history(request):
    try:
        # Get student directly using the username (which is admission number)
        student = Student.objects.get(registration_number=request.user.username)
    except ObjectDoesNotExist:
        return render(request, 'students/access_denied.html', {
            'message': 'No student record found matching your login credentials.'
        })
    
    # Get all fee records for this student, ordered by academic year and semester
    fee_records = StudentFee.objects.filter(student=student).select_related(
        'fee_structure__academic_year',
        'fee_structure__programme',
        'fee_structure'
    ).order_by(
        'fee_structure__academic_year__start_date',
        'fee_structure__semester'
    )
    
    # Organize data by academic year
    payment_history = {}
    total_paid = 0
    
    for record in fee_records:
        academic_year = record.fee_structure.academic_year
        semester = record.fee_structure.semester
        
        # Get all payments for this fee record
        payments = FeePayment.objects.filter(student_fee=record).order_by('payment_date')
        
        # Calculate total paid for this record
        paid_for_record = payments.aggregate(total=Sum('amount'))['total'] or 0
        total_paid += paid_for_record
        
        # Prepare the academic year entry if it doesn't exist
        if academic_year not in payment_history:
            payment_history[academic_year] = {
                'total_paid': 0,
                'semesters': {}
            }
        
        # Add semester data
        payment_history[academic_year]['semesters'][semester] = {
            'fee_structure': record.fee_structure,
            'expected_amount': record.fee_structure.amount,
            'paid_amount': paid_for_record,
            'balance': record.balance,
            'payments': payments,
            'is_complete': record.balance <= 0
        }
        
        # Update academic year total
        payment_history[academic_year]['total_paid'] += paid_for_record
    
    context = {
        'student': student,
        'payment_history': payment_history,
        'total_paid': total_paid,
        'semesters_per_year': student.programme.semesters_per_year,
    }
    
    return render(request, 'students/fee_history.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, StudentComment
from .forms import StudentCommentForm

@login_required
def student_comments(request):
    try:
        student = Student.objects.get(registration_number=request.user.username)
    except Student.DoesNotExist:
        return render(request, 'students/access_denied.html', {
            'message': 'No student record found matching your login credentials.'
        })
    
    if request.method == 'POST':
        form = StudentCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.student = student
            comment.save()
            messages.success(request, 'Your comment has been submitted successfully!')
            return redirect('student_comments')
    else:
        form = StudentCommentForm()
    
    comments = StudentComment.objects.filter(student=student).order_by('-created_at')
    
    context = {
        'student': student,
        'form': form,
        'comments': comments,
    }
    return render(request, 'comments/comments.html', context)


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import StudentComment
from .forms import AdminCommentResponseForm

def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_comment_dashboard(request):
    # Get all comments ordered by newest first
    comments = StudentComment.objects.all().order_by('-created_at').select_related('student')
    
    # Filter options
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'pending':
        comments = comments.filter(is_resolved=False)
    elif status_filter == 'resolved':
        comments = comments.filter(is_resolved=True)
    
    context = {
        'comments': comments,
        'status_filter': status_filter,
        'pending_count': StudentComment.objects.filter(is_resolved=False).count(),
        'resolved_count': StudentComment.objects.filter(is_resolved=True).count(),
        'total_count': StudentComment.objects.count(),
    }
    return render(request, 'comments/comments_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_comment_response(request, comment_id):
    comment = get_object_or_404(StudentComment, pk=comment_id)
    
    if request.method == 'POST':
        form = AdminCommentResponseForm(request.POST, instance=comment)
        if form.is_valid():
            response = form.save(commit=False)
            response.responded_by = request.user
            response.save()
            messages.success(request, 'Response submitted successfully!')
            return redirect('admin_comment_dashboard')
    else:
        form = AdminCommentResponseForm(instance=comment)
    
    context = {
        'comment': comment,
        'form': form,
    }
    return render(request, 'comments/comment_response.html', context)


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from students_portal.models import UnitAllocation, StudentEnrollment, Semester
from django.db.models import Prefetch

@login_required
def unit_students(request, unit_allocation_id=None):
    # Check if user is a lecturer
    if request.session.get('user_type') != 'lecturer':
        messages.error(request, "You don't have permission to view this page")
        return redirect('login')
    
    lecturer_id = request.session.get('lecturer_id')
    current_semester = Semester.objects.filter(is_current=True).first()
    
    # Get all units assigned to this lecturer
    lecturer_units = UnitAllocation.objects.filter(
        lecturer_id=lecturer_id,
        semester=current_semester
    ).select_related(
        'programme_unit__unit',
        'programme_unit__programme'
    )
    
    # If specific unit is requested
    if unit_allocation_id:
        unit_allocation = get_object_or_404(UnitAllocation, 
                                          id=unit_allocation_id,
                                          lecturer_id=lecturer_id)
        
        # Get enrolled students with related data
        enrollments = StudentEnrollment.objects.filter(
            programme_unit=unit_allocation.programme_unit,
            semester=current_semester
        ).select_related(
            'student',
            'student__programme'
        ).order_by('student__last_name', 'student__first_name')
        
        context = {
            'unit_allocation': unit_allocation,
            'enrollments': enrollments,
            'lecturer_units': lecturer_units,
            'current_semester': current_semester,
            'is_specific_unit': True,
        }
    else:
        # Show all units with student counts
        lecturer_units = lecturer_units.annotate(
            student_count=Count('programme_unit__enrollments',
                              filter=Q(programme_unit__enrollments__semester=current_semester)))
        
        context = {
            'lecturer_units': lecturer_units,
            'current_semester': current_semester,
            'is_specific_unit': False,
        }
    
    return render(request, 'lecturer/unit_students.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UnitAllocation, LectureNotes
from .forms import LectureNotesForm



@login_required
def upload_lecture_notes(request, unit_allocation_id=None):
    # Check if user is a lecturer
    if request.session.get('user_type') != 'lecturer':
        messages.error(request, "You don't have permission to access this page")
        return redirect('login')
    
    lecturer_id = request.session.get('lecturer_id')
    
    # Get all units assigned to this lecturer
    lecturer_units = UnitAllocation.objects.filter(
        lecturer_id=lecturer_id,
        semester__is_current=True
    ).select_related('programme_unit__unit')
    
    # If specific unit is selected
    selected_unit = None
    notes = None
    
    if unit_allocation_id:
        selected_unit = get_object_or_404(UnitAllocation, 
                                        id=unit_allocation_id,
                                        lecturer_id=lecturer_id)
        notes = LectureNotes.objects.filter(
            unit_allocation=selected_unit
        ).order_by('-date_uploaded')
    
    if request.method == 'POST':
        form = LectureNotesForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.unit_allocation = selected_unit
            note.save()
            messages.success(request, "Lecture notes uploaded successfully!")
            return redirect('upload_lecture_notes_unit', unit_allocation_id=unit_allocation_id)
    else:
        form = LectureNotesForm()
    
    context = {
        'lecturer_units': lecturer_units,
        'selected_unit': selected_unit,
        'notes': notes,
        'form': form,
    }
    return render(request, 'lecturer/upload_lecture_notes.html', context)


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import LectureNotes

@login_required
def delete_lecture_note(request, note_id):
    # Check if user is a lecturer
    if request.session.get('user_type') != 'lecturer':
        messages.error(request, "You don't have permission to perform this action")
        return redirect('login')
    
    # Get the note and verify ownership
    note = get_object_or_404(
        LectureNotes,
        id=note_id,
        unit_allocation__lecturer_id=request.session.get('lecturer_id')
    )
    
    if request.method == 'POST':
        unit_allocation_id = note.unit_allocation.id
        note.pdf_file.delete()  # Delete the file from storage
        note.delete()          # Delete the database record
        messages.success(request, "Lecture notes deleted successfully")
        return redirect('upload_lecture_notes_unit', unit_allocation_id=unit_allocation_id)
    
    # If not POST, show confirmation (handled via JavaScript in your template)
    messages.error(request, "Invalid request method")
    return redirect('upload_lecture_notes')


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import StudentEnrollment, LectureNotes

@login_required
def student_view_notes(request):
    # Check if user is a student
    if request.session.get('user_type') != 'student':
        messages.error(request, "You don't have permission to access this page")
        return redirect('login')
    
    student_id = request.session.get('student_id')
    current_semester = Semester.objects.filter(is_current=True).first()
    
    
    # Get all enrolled units for current semester
    enrollments = StudentEnrollment.objects.filter(
        student_id=student_id,
        semester=current_semester
    ).select_related('programme_unit__unit')
    
    # Get notes for these units and group by unit
    notes_by_unit = {}
    for enrollment in enrollments:
        unit = enrollment.programme_unit.unit
        notes = LectureNotes.objects.filter(
            unit_allocation__programme_unit=enrollment.programme_unit,
            is_published=True
        ).select_related(
            'unit_allocation__lecturer'
        ).order_by('-date_uploaded')
        
        if notes.exists():
            notes_by_unit[unit] = notes
    
    
    context = {
        'notes_by_unit': notes_by_unit,
        'current_semester': current_semester,
        'enrollments': enrollments,
        'notes': notes,
        # 'current_semester': current_semester,
    }
    return render(request, 'notes/view_notes.html', context)


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import UnitAllocation, StudentEnrollment, Semester, AttendanceRecord

@login_required
def lecturer_attendance_view(request):
    """Lecturer view of assigned units with attendance summary"""
    if request.session.get('user_type') != 'lecturer':
        return redirect('login')
    
    lecturer_id = request.session.get('lecturer_id')
    current_semester = Semester.objects.filter(is_current=True).first()
    
    # Get current week from semester (default to 1 if not set)
    current_week = current_semester.current_week if current_semester else 1
    
    # Get units with student counts and attendance weeks
    units = UnitAllocation.objects.filter(
        lecturer_id=lecturer_id,
        semester=current_semester
    ).annotate(
        student_count=Count('programme_unit__enrollments',
                          filter=Q(programme_unit__enrollments__semester=current_semester)),
        weeks_with_attendance=Count('attendance_records', distinct=True)
    ).select_related('programme_unit__unit')
    
    context = {
        'units': units,
        'current_semester': current_semester,
        'current_week': current_week,
        'total_weeks': 10  # Assuming 10-week semester
    }
    return render(request, 'attendance/lecturer_units.html', context)

@login_required
def lecturer_unit_attendance(request, unit_allocation_id):
    """Detailed attendance for a specific unit"""
    if request.session.get('user_type') != 'lecturer':
        return redirect('login')
    
    lecturer_id = request.session.get('lecturer_id')
    unit_allocation = get_object_or_404(
        UnitAllocation,
        id=unit_allocation_id,
        lecturer_id=lecturer_id
    )
    
    # Get all attendance records for this unit
    attendance_records = AttendanceRecord.objects.filter(
        unit_allocation=unit_allocation
    ).order_by('week_number').prefetch_related('student_attendances')
    
    # Get enrolled students
    students = StudentEnrollment.objects.filter(
        programme_unit=unit_allocation.programme_unit,
        semester=unit_allocation.semester
    ).select_related('student')
    
    # Current week
    current_semester = Semester.objects.filter(is_current=True).first()
    current_week = current_semester.current_week if current_semester else 1
    
    context = {
        'unit_allocation': unit_allocation,
        'attendance_records': attendance_records,
        'students': students,
        'current_week': current_week,
    }
    return render(request, 'attendance/lecturer_unit_details.html', context)


@login_required
def update_attendance(request, unit_allocation_id, week):
    """Update attendance for a specific week"""
    if request.session.get('user_type') != 'lecturer':
        return redirect('login')
    
    lecturer_id = request.session.get('lecturer_id')
    unit_allocation = get_object_or_404(
        UnitAllocation,
        id=unit_allocation_id,
        lecturer_id=lecturer_id
    )
    
    # Get or create attendance record
    record, created = AttendanceRecord.objects.get_or_create(
        unit_allocation=unit_allocation,
        week_number=week,
        defaults={
            'date': timezone.now().date(),
            'topic': f"Week {week} Lecture"
        }
    )
    
    # Update attendance for each student
    for student in StudentEnrollment.objects.filter(
        programme_unit=unit_allocation.programme_unit,
        semester=unit_allocation.semester
    ).select_related('student'):
        is_present = request.POST.get(f'student_{student.student.id}') == 'on'
        remarks = request.POST.get(f'remarks_{student.student.id}', '')
        
        StudentAttendance.objects.update_or_create(
            attendance_record=record,
            student_id=student.student.id,
            defaults={
                'is_present': is_present,
                'remarks': remarks
            }
        )
    
    messages.success(request, f"Week {week} attendance updated successfully!")
    return redirect('lecturer_unit_attendance', unit_allocation_id=unit_allocation.id)


@login_required
def student_attendance_view(request):
    """Student view of enrolled units with attendance"""
    if request.session.get('user_type') != 'student':
        return redirect('login')
    
    student_id = request.session.get('student_id')
    current_semester = Semester.objects.filter(is_current=True).first()
    
    # Get enrolled units with attendance summary
    enrollments = StudentEnrollment.objects.filter(
        student_id=student_id,
        semester=current_semester
    ).select_related(
        'programme_unit__unit',
        'programme_unit__programme'
    ).prefetch_related(
        Prefetch(
            'programme_unit__unit_allocations',
            queryset=UnitAllocation.objects.select_related('lecturer').prefetch_related(
                Prefetch(
                    'attendance_records',
                    queryset=AttendanceRecord.objects.order_by('week_number').prefetch_related(
                        Prefetch(
                            'student_attendances',
                            queryset=StudentAttendance.objects.filter(student_id=student_id)
                    )
                )
            )
        )
    )
    )
    
    current_week = current_semester.current_week if current_semester else 1
    
    context = {
        'enrollments': enrollments,
        'current_week': current_week,
    }
    return render(request, 'attendance/student_units.html', context)


@login_required
def student_attendance_history(request, unit_allocation_id):
    """View showing a student's attendance history for a specific unit"""
    if request.session.get('user_type') != 'student':
        return redirect('login')
    
    student_id = request.session.get('student_id')
    
    # Verify the student is enrolled in this unit
    enrollment = get_object_or_404(
        StudentEnrollment,
        student_id=student_id,
        programme_unit__unit_allocations__id=unit_allocation_id
    )
    
    # Get the unit allocation and all attendance records
    unit_allocation = get_object_or_404(
        UnitAllocation,
        id=unit_allocation_id,
        programme_unit=enrollment.programme_unit
    )
    
    # Get all attendance records with this student's attendance
    attendance_records = AttendanceRecord.objects.filter(
        unit_allocation=unit_allocation
    ).order_by('week_number').prefetch_related(
        Prefetch(
            'student_attendances',
            queryset=StudentAttendance.objects.filter(student_id=student_id)
    )
    )
    
    # Calculate attendance statistics
    total_weeks = attendance_records.count()
    present_count = sum(1 for r in attendance_records if r.student_attendances.all())
    attendance_percentage = (present_count / total_weeks * 100) if total_weeks > 0 else 0
    
    context = {
        'unit_allocation': unit_allocation,
        'attendance_records': attendance_records,
        'total_weeks': total_weeks,
        'present_count': present_count,
        'attendance_percentage': attendance_percentage,
        'student': enrollment.student,
    }
    return render(request, 'attendance/student_history.html', context)



@login_required
def student_sign_attendance(request, unit_allocation_id):
    """View for students to sign attendance for current week"""
    if request.session.get('user_type') != 'student':
        return redirect('login')
    
    student_id = request.session.get('student_id')
    current_semester = Semester.objects.filter(is_current=True).first()
    
    # Verify enrollment and get unit allocation
    enrollment = get_object_or_404(
        StudentEnrollment,
        student_id=student_id,
        programme_unit__unit_allocations__id=unit_allocation_id,
        semester=current_semester
    )
    
    unit_allocation = get_object_or_404(
        UnitAllocation,
        id=unit_allocation_id,
        programme_unit=enrollment.programme_unit
    )
    
    current_week = current_semester.current_week if current_semester else 1
    
    # Handle form submission
    if request.method == 'POST':
        # Get or create attendance record
        record, created = AttendanceRecord.objects.get_or_create(
            unit_allocation=unit_allocation,
            week_number=current_week,
            defaults={
                'date': timezone.now().date(),
                'topic': f"Week {current_week} Lecture"
            }
        )
        
        # Create or update attendance
        StudentAttendance.objects.update_or_create(
            attendance_record=record,
            student_id=student_id,
            defaults={
                'is_present': True,
                'remarks': 'Signed by student'
            }
        )
        
        messages.success(request, "Attendance signed successfully!")
        return redirect('student_attendance_view')
    
    # Check if already signed
    already_signed = AttendanceRecord.objects.filter(
        unit_allocation=unit_allocation,
        week_number=current_week,
        student_attendances__student_id=student_id
    ).exists()
    
    context = {
        'unit_allocation': unit_allocation,
        'current_week': current_week,
        'already_signed': already_signed,
        'student': enrollment.student,
    }
    return render(request, 'attendance/student_sign.html', context)



# views.py
import jwt
from datetime import datetime, timedelta
from .utils import calculate_distance


# views.py
@login_required
def lecturer_generate_qr(request, unit_allocation_id):
    """Display QR generation page and handle AJAX requests"""
    if request.session.get('user_type') != 'lecturer':
        return redirect('login')
    
    unit = get_object_or_404(UnitAllocation, id=unit_allocation_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle AJAX QR generation
        try:
            lat = float(request.GET.get('lat'))
            lng = float(request.GET.get('lng'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid location'}, status=400)
        
        # In views.py
        payload = {
            'u': unit_allocation_id,  # Shortened keys
            'l': request.user.id,
            'loc': f"{lat},{lng}",  # Combine coordinates
            'exp': datetime.utcnow() + timedelta(minutes=15)
        }
        qr_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        session = QRAttendanceSession.objects.create(
            unit_allocation=unit,
            lecturer_id=request.session.get('lecturer_id'),
            qr_token=qr_token,
            valid_from=datetime.now(),
            valid_to=datetime.now() + timedelta(minutes=15),
            latitude=lat,
            longitude=lng,
            max_distance_km=0.05  # 50 meters
        )
        
        return JsonResponse({
            'qr_token': qr_token,
            'expires_at': session.valid_to.isoformat()
        })
    
    # Regular GET request - show QR page
    context = {
        'unit': unit,
        'current_semester': unit.semester
    }
    return render(request, 'attendance/lecturer_generate_qr.html', context)

@login_required
def student_scan_qr(request):
    """Handle QR code attendance scanning for students"""
    """Render scan page for GET, handle POST scans"""
    if request.method == 'GET':
        return render(request, 'attendance/student_scan.html')
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        # Get data from student's device
        qr_token = request.POST.get('qr_token')
        student_lat = float(request.POST.get('lat'))
        student_lng = float(request.POST.get('lng'))
        device_fp = request.POST.get('device_fp')
        
        # 1. Verify JWT token
        try:
            payload = jwt.decode(qr_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'QR code expired'}, status=400)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid QR code'}, status=400)
        
        # 2. Verify session exists and is valid
        try:
            session = QRAttendanceSession.objects.get(
                qr_token=qr_token,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            )
        except QRAttendanceSession.DoesNotExist:
            return JsonResponse({'error': 'Invalid or expired session'}, status=400)
        
        # 3. Verify location
        distance_km = calculate_distance(
            float(session.latitude),
            float(session.longitude),
            student_lat,
            student_lng
        )
        
        if distance_km > float(session.max_distance_km):
            return JsonResponse({
                'error': f'You must be within {session.max_distance_km*1000:.0f}m of classroom',
                'distance': f'{distance_km*1000:.0f}m'
            }, status=400)
        
        # 4. Prevent duplicate scans
        if QRAttendanceLog.objects.filter(
            session=session,
            device_fingerprint=device_fp
        ).exists():
            return JsonResponse({'error': 'This device already scanned'}, status=400)
        
        if QRAttendanceLog.objects.filter(
            session=session,
            student=request.user.student
        ).exists():
            return JsonResponse({'error': 'Attendance already recorded'}, status=400)
        
        # 5. Create attendance log
        QRAttendanceLog.objects.create(
            session=session,
            student=request.user.student,
            device_fingerprint=device_fp,
            scan_latitude=student_lat,
            scan_longitude=student_lng
        )
        
        # 6. Record in main attendance system
        week = session.unit_allocation.semester.get_current_week()
        
        # Get or create attendance record
        record, created = AttendanceRecord.objects.get_or_create(
            unit_allocation=session.unit_allocation,
            week_number=week,
            defaults={
                'date': timezone.now().date(),
                'topic': f"Week {week} QR Attendance",
                'is_locked': False
            }
        )
        
        # Update student attendance
        StudentAttendance.objects.update_or_create(
            attendance_record=record,
            student=request.user.student,
            defaults={
                'is_present': True,
                'remarks': f"QR verified at {distance_km*1000:.0f}m from class"
            }
        )
        
        # Return success
        return JsonResponse({
            'success': 'Attendance recorded!',
            'unit': session.unit_allocation.programme_unit.unit.code,
            'week': week,
            'distance': f'{distance_km*1000:.0f}m'
        })
    
    except ValueError:
        return JsonResponse({'error': 'Invalid location data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

#function to generate timetables automatically
from django.db import transaction
from datetime import time
import random

def generate_timetable(semester_id, programme_id, year_of_study):
    """
    Automatically generates a timetable for a given programme and year of study in a semester
    """
    # Get all required objects
    semester = Semester.objects.get(pk=semester_id)
    programme = Programme.objects.get(pk=programme_id)
    
    # Get all units for this programme/year/semester
    units = ProgrammeUnit.objects.filter(
        programme=programme,
        year_of_study=year_of_study,
        semester=semester.number
    ).select_related('unit')
    
    # Get all available lecture halls
    lecture_halls = list(LectureHall.objects.all())
    
    # Define standard time slots (can be customized)
    time_slots = [
        # Morning slots
        {'start': time(8, 0), 'end': time(10, 0), 'day': 0},  # Monday
        {'start': time(10, 0), 'end': time(12, 0), 'day': 0},
        {'start': time(8, 0), 'end': time(10, 0), 'day': 1},   # Tuesday
        {'start': time(10, 0), 'end': time(12, 0), 'day': 1},
        {'start': time(8, 0), 'end': time(10, 0), 'day': 2},   # Wednesday
        {'start': time(10, 0), 'end': time(12, 0), 'day': 2},
        {'start': time(8, 0), 'end': time(10, 0), 'day': 3},   # Thursday
        {'start': time(10, 0), 'end': time(12, 0), 'day': 3},
        {'start': time(8, 0), 'end': time(10, 0), 'day': 4},   # Friday
        {'start': time(10, 0), 'end': time(12, 0), 'day': 4},
        # Afternoon slots
        {'start': time(14, 0), 'end': time(16, 0), 'day': 0},
        {'start': time(16, 0), 'end': time(18, 0), 'day': 0},
        {'start': time(14, 0), 'end': time(16, 0), 'day': 1},
        {'start': time(16, 0), 'end': time(18, 0), 'day': 1},
        {'start': time(14, 0), 'end': time(16, 0), 'day': 2},
        {'start': time(16, 0), 'end': time(18, 0), 'day': 2},
        {'start': time(14, 0), 'end': time(16, 0), 'day': 3},
        {'start': time(16, 0), 'end': time(18, 0), 'day': 3},
        {'start': time(14, 0), 'end': time(16, 0), 'day': 4},
        {'start': time(16, 0), 'end': time(18, 0), 'day': 4},
    ]
    
    # Create or get the timetable
    timetable, created = Timetable.objects.get_or_create(
        semester=semester,
        programme=programme,
        year_of_study=year_of_study
    )
    
    # Clear existing scheduled lessons if regenerating
    timetable.scheduled_lessons.all().delete()
    
    # Get all unit allocations for these units in this semester
    unit_allocations = UnitAllocation.objects.filter(
        programme_unit__in=units,
        semester=semester
    ).select_related('lecturer', 'programme_unit__unit')
    
    with transaction.atomic():
        # Create TimeSlot objects if they don't exist
        for slot in time_slots:
            time_slot_obj, _ = TimeSlot.objects.get_or_create(
                start_time=slot['start'],
                end_time=slot['end'],
                day_of_week=slot['day']
            )
        
        # Get all available time slots
        all_time_slots = TimeSlot.objects.all().order_by('day_of_week', 'start_time')
        
        # Assign units to time slots
        scheduled_lessons = []
        for allocation in unit_allocations:
            # Each unit typically has 2-3 sessions per week
            sessions_per_week = 2 if allocation.programme_unit.unit.credit_hours <= 3 else 3
            
            # Find available time slots
            available_slots = list(all_time_slots)
            random.shuffle(available_slots)  # Randomize to create varied timetables
            
            assigned_slots = 0
            for slot in available_slots:
                if assigned_slots >= sessions_per_week:
                    break
                
                # Check if this slot is already taken in this timetable
                conflict_exists = ScheduledLesson.objects.filter(
                    timetable=timetable,
                    time_slot=slot
                ).exists()
                
                if not conflict_exists:
                    # Assign a random lecture hall
                    hall = random.choice(lecture_halls)
                    
                    scheduled_lessons.append(ScheduledLesson(
                        timetable=timetable,
                        unit_allocation=allocation,
                        time_slot=slot,
                        lecture_hall=hall,
                        frequency='weekly'
                    ))
                    assigned_slots += 1
            
            # If we couldn't find enough slots, this generation failed
            if assigned_slots < sessions_per_week:
                raise ValueError(f"Could not find enough time slots for {allocation.programme_unit.unit.code}")
        
        # Bulk create all scheduled lessons
        ScheduledLesson.objects.bulk_create(scheduled_lessons)
    
    return timetable



def view_timetable(semester_id, programme_id, year_of_study):
    try:
        timetable = Timetable.objects.get(
            semester_id=semester_id,
            programme_id=programme_id,
            year_of_study=year_of_study
        )
    except Timetable.DoesNotExist:
        return None  # or return an empty dict {}
    
    lessons = timetable.scheduled_lessons.select_related(
        'unit_allocation__programme_unit__unit',
        'unit_allocation__lecturer',
        'time_slot',
        'lecture_hall'
    ).order_by('time_slot__day_of_week', 'time_slot__start_time')
    
    # Group by day for display
    timetable_data = {}
    for lesson in lessons:
        day = lesson.time_slot.get_day_of_week_display()
        if day not in timetable_data:
            timetable_data[day] = []
        
        timetable_data[day].append({
            'unit_code': lesson.unit_allocation.programme_unit.unit.code,
            'unit_name': lesson.unit_allocation.programme_unit.unit.name,
            'lecturer': lesson.unit_allocation.lecturer.get_full_name(),
            'time': f"{lesson.time_slot.start_time.strftime('%H:%M')}-{lesson.time_slot.end_time.strftime('%H:%M')}",
            'hall': lesson.lecture_hall.name
        })
    
    return timetable_data


from django.shortcuts import render
from django.http import JsonResponse
from .models import Semester, Programme

def timetable_view(request):
    template_name = 'timetable.html'

    if request.method == 'GET':
        semesters = Semester.objects.filter(is_current=True)
        current_year = semesters.first().academic_year if semesters.exists() else None
        programmes = Programme.objects.all()
        
        # Initialize with empty year options - they'll be loaded via AJAX
        year_options = []

        return render(request, template_name, {
            'semesters': semesters,
            'programmes': programmes,  # Note: using 'programmes' in template
            'current_year': current_year,
            'year_options': year_options,  # Not used directly in the new approach
        })

    elif request.method == 'POST':
        # Handle AJAX request for year options
        if request.POST.get('action') == 'get_years':
            programme_id = request.POST.get('programme_id')
            try:
                programme = Programme.objects.get(id=programme_id)
                year_options = list(range(1, programme.duration_years + 1))
                return JsonResponse({
                    'success': True,
                    'year_options': year_options,
                    'programme_name': programme.name
                })
            except Programme.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Programme not found'})
        
        # Handle form submission for timetable
        semester_id = request.POST.get('semester_id')
        programme_id = request.POST.get('programme_id')
        year_of_study = request.POST.get('year_of_study')

        if not all([semester_id, programme_id, year_of_study]):
            return JsonResponse({'success': False, 'error': 'Missing required fields'})

        try:
            timetable_data = view_timetable(semester_id, programme_id, year_of_study)
            if not timetable_data:
                try:
                    generate_timetable(semester_id, programme_id, year_of_study)
                    timetable_data = view_timetable(semester_id, programme_id, year_of_study)
                    return JsonResponse({'success': True, 'timetable': timetable_data})
                except Exception as gen_error:
                    return JsonResponse({
                        'success': False,
                        'error': f'Timetable generation failed: {str(gen_error)}'
                    })
            return JsonResponse({'success': True, 'timetable': timetable_data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Semester, ScheduledLesson, StudentEnrollment

@login_required
def student_timetable(request):
    # Get current student and semester
    student = Student.objects.get(registration_number=request.user.username)
    current_semester = Semester.objects.filter(is_current=True).first()
    
    if not current_semester:
        return render(request, 'student_timetable.html', {
            'error': 'No current semester found'
        })
    
    # Get the student's enrollment for current semester
    enrollment = StudentEnrollment.objects.filter(
        student=student,
        semester=current_semester
    ).first()
    
    if not enrollment:
        return render(request, 'student_timetable.html', {
            'error': 'You are not enrolled in any programme for this semester'
        })
    
    # Get the programme from programme_unit
    programme = enrollment.programme_unit.programme
    
    # Get the timetable for their programme and year
    timetable = Timetable.objects.filter(
        semester=current_semester,
        programme=programme,
        year_of_study=enrollment.programme_unit.year_of_study,
        is_published=True
    ).first()
    
    if not timetable:
        return render(request, 'student_timetable.html', {
            'error': 'Timetable not available for your programme'
        })
    
    # Get all scheduled lessons for this timetable
    scheduled_lessons = ScheduledLesson.objects.filter(
        timetable=timetable
    ).select_related(
        'unit_allocation__programme_unit__unit',
        'time_slot',
        'lecture_hall'
    ).order_by('time_slot__day_of_week', 'time_slot__start_time')
    
    # Get day choices from TimeSlot model
    day_choices = TimeSlot._meta.get_field('day_of_week').choices
    days_of_week = {value: label for value, label in day_choices}
    
    # Initialize timetable data structure
    timetable_data = {day: {} for day in days_of_week.values()}
    
    # Get all unique time slots for this timetable
    time_slots = TimeSlot.objects.filter(
        scheduled_lessons__timetable=timetable
    ).distinct().order_by('start_time')
    
    # Populate timetable data
    for lesson in scheduled_lessons:
        day_name = lesson.time_slot.get_day_of_week_display()
        time_range = f"{lesson.time_slot.start_time.strftime('%H:%M')}-{lesson.time_slot.end_time.strftime('%H:%M')}"
        
        timetable_data[day_name][time_range] = {
            'unit_code': lesson.unit_allocation.programme_unit.unit.code,
            'unit_name': lesson.unit_allocation.programme_unit.unit.name,
            'lecture_hall': lesson.lecture_hall.name,
            'lecturer': lesson.unit_allocation.lecturer.get_full_name(),
        }
    
    context = {
        'current_semester': current_semester,
        'programme': programme,
        'year_of_study': enrollment.programme_unit.year_of_study,
        'days_of_week': days_of_week.values(),
        'time_slots': time_slots,
        'timetable_data': timetable_data,
    }
    
    return render(request, 'student_timetable.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import (
    Lecturer, ProgrammeUnit, Semester, UnitAllocation,
    AcademicYear, Department
)

def unit_allocation_view(request):
    # Get current academic year and semester
    try:
        current_academic_year = AcademicYear.objects.get(is_current=True)
        current_semester = Semester.objects.filter(
            academic_year=current_academic_year,
            is_current=True
        ).first()
        
        if not current_semester:
            messages.error(request, "No current semester set in the system")
            return redirect('admin_dashboard')
    except AcademicYear.DoesNotExist:
        messages.error(request, "No current academic year set in the system")
        return redirect('admin_dashboard')

    # Get all departments
    departments = Department.objects.all()
    
    # Handle department filter - convert "None" string to None
    selected_department_id = request.GET.get('department')
    if selected_department_id == 'None':
        selected_department_id = None
    
    # Get all lecturers (filter by department if selected)
    lecturers_query = Lecturer.objects.filter(is_active=True)
    if selected_department_id:
        try:
            selected_department_id = int(selected_department_id)
            lecturers_query = lecturers_query.filter(department_id=selected_department_id)
        except (ValueError, TypeError):
            messages.error(request, "Invalid department selected")
            return redirect('unit_allocation')
    
    lecturers = lecturers_query.select_related('department').order_by('last_name')

    # Handle lecturer selection
    selected_lecturer_id = request.GET.get('lecturer')
    selected_lecturer = None
    programme_units = []
    existing_allocations = []

    if selected_lecturer_id:
        try:
            selected_lecturer = Lecturer.objects.get(
                id=selected_lecturer_id,
                is_active=True
            )
            
            # Get all programme units for current semester
            programme_units = ProgrammeUnit.objects.filter(
                semester=current_semester.number
            ).select_related('unit', 'programme', 'programme__department')
            
            # Filter by lecturer's department if needed
            if selected_department_id:
                programme_units = programme_units.filter(
                    programme__department=selected_lecturer.department
                )
            
            # Get existing allocations for this lecturer in current semester
            existing_allocations = UnitAllocation.objects.filter(
                lecturer=selected_lecturer,
                semester=current_semester
            ).values_list('programme_unit_id', flat=True)

        except Lecturer.DoesNotExist:
            messages.error(request, "Selected lecturer not found")
            return redirect('unit_allocation')
        except ValueError:
            messages.error(request, "Invalid lecturer ID")
            return redirect('unit_allocation')

    # ... rest of your view code ...

    # Handle form submission
    if request.method == 'POST':
        if not selected_lecturer:
            messages.error(request, "Please select a lecturer first")
            return redirect('unit_allocation')
        
        # Get selected units from form
        selected_unit_ids = request.POST.getlist('units')
        
        try:
            # Validate selected units exist in current semester
            valid_units = ProgrammeUnit.objects.filter(
                id__in=selected_unit_ids,
                semester=current_semester.number
            )
            
            if len(valid_units) != len(selected_unit_ids):
                messages.error(request, "Some selected units are invalid")
                return redirect('unit_allocation')
            
            # Create new allocations
            new_allocations = []
            for unit in valid_units:
                # Check if allocation already exists
                if not UnitAllocation.objects.filter(
                    programme_unit=unit,
                    semester=current_semester
                ).exists():
                    new_allocations.append(UnitAllocation(
                        lecturer=selected_lecturer,
                        programme_unit=unit,
                        semester=current_semester
                    ))
            
            # Bulk create new allocations
            if new_allocations:
                UnitAllocation.objects.bulk_create(new_allocations)
                messages.success(request, f"Successfully allocated {len(new_allocations)} units")
            else:
                messages.info(request, "No new units were allocated")
            
            return redirect('unit_allocation')
        
        except Exception as e:
            messages.error(request, f"Error allocating units: {str(e)}")
            return redirect('unit_allocation')

    context = {
        'current_academic_year': current_academic_year,
        'current_semester': current_semester,
        'departments': departments,
        'selected_department_id': int(selected_department_id) if selected_department_id else None,
        'lecturers': lecturers,
        'selected_lecturer': selected_lecturer,
        'programme_units': programme_units,
        'existing_allocations': existing_allocations,
    }
    
    return render(request, 'units/unit_allocation.html', context)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import (
    Student, StudentEnrollment, StudentUnitGrade, ProgrammeUnit,
    Semester, AcademicYear
)
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from .models import (
    Student, StudentEnrollment, StudentUnitGrade, ProgrammeUnit,
    Semester, AcademicYear, SpecialExamApplication, AppliedExamUnit, Unit
)
from django.conf import settings
from django.core.mail import EmailMessage

@login_required
def special_exam_application(request):
    # Get current student
    try:
        student = Student.objects.get(registration_number=request.user.username)
    except Student.DoesNotExist:
        messages.error(request, "Student record not found")
        return redirect('student_dashboard')
    
    # Get current academic year and semester
    try:
        current_academic_year = AcademicYear.objects.get(is_current=True)
        current_semester = Semester.objects.get(
            academic_year=current_academic_year,
            is_current=True
        )
    except (AcademicYear.DoesNotExist, Semester.DoesNotExist):
        messages.error(request, "Current semester information not available")
        return redirect('student_dashboard')
    
    # Get all failed units for this student
    failed_units = StudentUnitGrade.objects.filter(
        enrollment__student=student,
        is_pass=False
    ).select_related(
        'enrollment__programme_unit__unit',
        'enrollment__programme_unit__programme',
        'enrollment__semester'
    )
    
    # Categorize failed units
    failed_in_current_semester = []
    failed_in_previous_semesters = []
    supplementary_eligible = []
    special_exam_eligible = []
    
    for grade in failed_units:
        unit_info = {
            'id': grade.id,
            'unit_id': grade.enrollment.programme_unit.unit.id,
            'unit_code': grade.enrollment.programme_unit.unit.code,
            'unit_name': grade.enrollment.programme_unit.unit.name,
            'semester_taken': grade.enrollment.semester,
            'year_taken': grade.enrollment.programme_unit.year_of_study,
            'semester_taken_number': grade.enrollment.programme_unit.semester,
            'grade': grade.grade.grade if grade.grade else 'F',
            'score': grade.total_score,
            'is_current': grade.enrollment.semester == current_semester,
            'enrollment_id': grade.enrollment.id,
            'grade_id': grade.id,
        }
        
        if unit_info['is_current']:
            failed_in_current_semester.append(unit_info)
        else:
            failed_in_previous_semesters.append(unit_info)
    
    # Check if student qualifies for special exams (failed > 3 units in one semester)
    semester_failure_counts = {}
    for unit in failed_in_previous_semesters + failed_in_current_semester:
        semester_key = f"{unit['semester_taken']}"
        semester_failure_counts[semester_key] = semester_failure_counts.get(semester_key, 0) + 1
    
    qualifies_for_special = any(count > 3 for count in semester_failure_counts.values())
    
    # Find which failed units are being offered in current semester
    current_offered_units = ProgrammeUnit.objects.filter(
        semester=current_semester.number
    ).values_list('unit__code', flat=True)
    
    # Categorize units based on eligibility
    for unit in failed_in_previous_semesters + failed_in_current_semester:
        if unit['unit_code'] in current_offered_units:
            if qualifies_for_special:
                special_exam_eligible.append(unit)
            else:
                supplementary_eligible.append(unit)
    
    # Handle form submission
    # Handle form submission
    if request.method == 'POST':
        selected_units = request.POST.getlist('units')
        application_type = request.POST.get('application_type')
        
        # Validate selected units
        # Create a dictionary of all eligible units for easier lookup
        all_eligible_units = {str(u['id']): u for u in supplementary_eligible + special_exam_eligible}
        valid_unit_ids = all_eligible_units.keys()
        
        invalid_units = [unit for unit in selected_units if unit not in valid_unit_ids]
        
        if invalid_units:
            messages.error(request, "Invalid unit selection")
            return redirect('special_exam_application')
        
        if not selected_units:
            messages.warning(request, "Please select at least one unit")
            return redirect('special_exam_application')
        
        # Check if already applied for any of these units
        already_applied = AppliedExamUnit.objects.filter(
            original_grade_id__in=[all_eligible_units[unit_id]['grade_id'] for unit_id in selected_units],
            application__student=student,
            application__semester=current_semester
        ).exists()
        
        if already_applied:
            messages.error(request, "You have already applied for one or more of these units")
            return redirect('special_exam_application')
        
        # Process application
        try:
            with transaction.atomic():
                # Create the application
                application = SpecialExamApplication.objects.create(
                    student=student,
                    semester=current_semester,
                    application_type=application_type,
                    payment_amount=800 * len(selected_units),
                )
                
                # Add selected units to the application
                for unit_id in selected_units:
                    unit_info = all_eligible_units[unit_id]
                    AppliedExamUnit.objects.create(
                        application=application,
                        unit_id=unit_info['unit_id'],
                        original_enrollment_id=unit_info['enrollment_id'],
                        original_grade_id=unit_info['grade_id'],
                    )
                
                # Generate and send PDF receipt
                pdf_buffer = application.generate_pdf_receipt()
                
                email = EmailMessage(
                    f"Exam Application Receipt - {application.get_application_type_display()}",
                    f"Dear {student.get_full_name()},\n\n"
                    f"Please find attached your {application.get_application_type_display()} application receipt.\n"
                    f"Verification Code: {application.verification_code}\n"
                    f"Total Amount: KSH {application.payment_amount:.2f}\n\n"
                    "Payment Instructions:\n"
                    "1. M-Pesa Paybill: 123456\n"
                    "2. Account: Your Registration Number\n"
                    "3. Amount: KSH 800 per unit\n\n"
                    "Thank you,\n"
                    "Examinations Office\n"
                    "Muranga University of Technology",
                    settings.DEFAULT_FROM_EMAIL,
                    [student.email],
                )
                email.attach(
                    f"exam_application_{application.id}.pdf",
                    pdf_buffer.getvalue(),
                    'application/pdf'
                )
                email.send()
                
                messages.success(
                    request,
                    f"{application.get_application_type_display()} application submitted successfully! "
                    f"A receipt has been sent to your email. Verification code: {application.verification_code}"
                )
                
        except Exception as e:
            messages.error(request, f"Error creating application: {str(e)}")
            # Log the full error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in special_exam_application: {str(e)}", exc_info=True)
        
        return redirect('special_exam_application')
    
    # ... [rest of the view remains the same] ...
    
    # Get already applied units to disable checkboxes
    applied_unit_ids = AppliedExamUnit.objects.filter(
        application__student=student,
        application__semester=current_semester
    ).values_list('original_grade_id', flat=True)
    
    context = {
        'student': student,
        'current_semester': current_semester,
        'failed_in_current_semester': failed_in_current_semester,
        'failed_in_previous_semesters': failed_in_previous_semesters,
        'supplementary_eligible': supplementary_eligible,
        'special_exam_eligible': special_exam_eligible,
        'qualifies_for_special': qualifies_for_special,
        'total_failed_units': len(failed_in_current_semester) + len(failed_in_previous_semesters),
        'applied_unit_ids': list(applied_unit_ids),
    }
    
    return render(request, 'students/special_exam_application.html', context)


@login_required
def verify_exam_payment(request):
    """View for students to verify their payment with the code"""
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code', '').strip().upper()
        
        try:
            application = SpecialExamApplication.objects.get(
                verification_code=verification_code,
                student__registration_number=request.user.username
            )
            
            if not application.is_code_valid():
                messages.error(request, "This verification code has expired")
                return redirect('verify_exam_payment')
            
            # Update application status
            application.status = 'paid'
            application.save()
            
            messages.success(request, "Payment verified successfully! Your application is now being processed.")
            return redirect('student_dashboard')
            
        except SpecialExamApplication.DoesNotExist:
            messages.error(request, "Invalid verification code")
    
    return render(request, 'students/verify_payment.html')