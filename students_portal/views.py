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
        uid = force_str(urlsafe_base64_decode(uidb64))  # Replace force_text with force_str
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password reset successful. You can now login with your new password.')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect('reset_password', uidb64=uidb64, token=token)
        return render(request, 'auth/reset_password.html')
    else:
        messages.error(request, 'Invalid reset link. Please try again.')
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

from django.db.models import Sum
from datetime import datetime
@login_required
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
    Displays lecturer profile information and academic details.
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
        
        # Fetch related department information
        department = lecturer.department
        
        context = {
            'lecturer': lecturer,
            'department': department,
            'page_title': 'Lecturer Dashboard',
        }
        
        return render(request, 'dashboards/lecturer_dashboard.html', context)
    
    except Lecturer.DoesNotExist:
        messages.error(request, "Lecturer profile not found. Please contact administration.")
        return redirect('login')

def prepare_gender_data_by_academic_year(academic_year_id):
    """Helper function to prepare gender distribution data for a specific academic year"""
    try:
        academic_year = AcademicYear.objects.get(id=academic_year_id)
        
        # Define gender mapping
        GENDER_MAPPING = {
            'M': 'Male',
            'F': 'Female',
            'O': 'Other'
        }
        
        # Filter students admitted during this academic year
        gender_counts = Student.objects.filter(
            date_of_admission__gte=academic_year.start_date,
            date_of_admission__lte=academic_year.end_date
        ).values('gender').annotate(count=Count('id'))
        
        # Process results
        if not gender_counts.exists():
            gender_data = [
                {'value': 0, 'name': 'Male'},
                {'value': 0, 'name': 'Female'},
                {'value': 0, 'name': 'Other'}
            ]
        else:
            gender_data = []
            for g in gender_counts:
                gender_name = GENDER_MAPPING.get(g['gender'], 'Other')
                gender_data.append({
                    'value': g['count'],
                    'name': gender_name
                })
        
        # Ensure all gender categories are present
        existing_genders = {g['name'] for g in gender_data}
        for gender in ['Male', 'Female', 'Other']:
            if gender not in existing_genders:
                gender_data.append({'value': 0, 'name': gender})
        
        return gender_data
        
    except AcademicYear.DoesNotExist:
        return [
            {'value': 0, 'name': 'Male'},
            {'value': 0, 'name': 'Female'},
            {'value': 0, 'name': 'Other'}
        ]


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
        
        academic_year_labels.append(academic_year.name)  # e.g. "2021/2022"
        academic_year_data.append(count)

    # Student statistics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='active').count()
    
    # Lecturer statistics
    total_lecturers = Lecturer.objects.count()
    active_lecturers = Lecturer.objects.filter(status='active').count()
    
    # Programme statistics
    total_programmes = Programme.objects.count()
    
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
    
    # Prepare data for charts
    admission_year_labels = []
    admission_year_data = []
    
    # Student population trend (last 5 years)
    current_year = datetime.now().year
    year_range = range(current_year - 4, current_year + 1)
    population_trend_labels = list(year_range)
    population_trend_data = []
    
    for year in year_range:
        count = Student.objects.filter(
            date_of_admission__year__lte=year
        ).count()
        population_trend_data.append(count)
    
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
        
        # Latest records
        'latest_students': latest_students,
        'latest_lecturers': latest_lecturers,
        
        # Chart data
        'academic_year_labels': json.dumps(academic_year_labels),
        'academic_year_data': json.dumps(academic_year_data),
        'admission_year_labels': json.dumps(admission_year_labels),
        'admission_year_data': json.dumps(admission_year_data),
        'population_trend_labels': json.dumps(population_trend_labels),
        'population_trend_data': json.dumps(population_trend_data),
        'gender_data': json.dumps(gender_data),
        
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
    academic_years = AcademicYear.objects.filter(
        start_date__gte=student.date_of_admission,
        semesters__id__isnull=False  # ✅ Ensures there's at least one linked semester
    ).distinct().order_by('-start_date')  # Order by latest year first (descending)

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
    """
    # Get all enrollments for the student ordered by semester
    enrollments = StudentEnrollment.objects.filter(
        student=student
    ).select_related(
        'semester__academic_year',
        'programme_unit__unit',
        'programme_unit__programme',
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
        final_grade = enrollment.final_grade
        
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
        
        # Add unit information
        unit_data = {
            'code': unit.code,
            'name': unit.name,
            'credit_hours': unit.credit_hours,
            'is_core': unit.is_core,
            'year_of_study': programme_unit.year_of_study,
            'semester': programme_unit.semester,
            'cat_average': final_grade.cat_average if final_grade else None,
            'exam_score': final_grade.exam_score if final_grade else None,
            'total_score': final_grade.total_score if final_grade else None,
            'grade': final_grade.grade.grade if final_grade and final_grade.grade else None,
            'is_pass': final_grade.is_pass if final_grade else None
        }
        
        progress_data['academic_years'][academic_year.id]['semesters'][semester.number]['units'].append(unit_data)
        
        # Update semester summary
        if final_grade:
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
                if unit['grade'] and unit['is_pass']:
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
from .models import Student, StudentUnitGrade, StudentFee

@login_required
@user_passes_test(lambda u: u.is_staff)
def promote_students(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                promoted_count = 0
                failed_promotion = 0
                
                # Get all active students
                active_students = Student.objects.filter(status='active')
                
                for student in active_students:
                    # Check if student has failed more than 3 units in current academic year
                    failed_units = StudentUnitGrade.objects.filter(
                        enrollment__student=student,
                        is_pass=False
                    ).count()
                    
                    # Check if student has any fee balance
                    has_balance = StudentFee.objects.filter(
                        student=student,
                        balance__gt=0
                    ).exists()
                    
                    if failed_units <= 3 and not has_balance:
                        # Promote the student
                        if student.current_semester == 2:
                            # Move to next year
                            student.current_year += 1
                            student.current_semester = 1
                        else:
                            # Move to next semester
                            student.current_semester += 1
                        
                        student.save()
                        promoted_count += 1
                    else:
                        failed_promotion += 1
                
                messages.success(request, f"Promotion complete! {promoted_count} students promoted. {failed_promotion} students didn't meet requirements.")
                return redirect('promote_students')
                
        except Exception as e:
            messages.error(request, f"Error during promotion: {str(e)}")
            return redirect('promote_students')
    
    # For GET requests, show promotion page with button
    return render(request, 'academics/admin/promote_students.html')
