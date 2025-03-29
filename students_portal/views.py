from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *


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


from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, Lecturer

User = get_user_model()

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
    Displays student profile information and academic details.
    """
    # Check if user is a student
    if request.session.get('user_type') != 'student':
        messages.error(request, "You don't have access to the student dashboard.")
        return redirect('login')
    
    # Get student id from session
    student_id = request.session.get('student_id')
    
    try:
        # Fetch the student record
        student = Student.objects.get(id=student_id)
        
        # Fetch related programme information
        programme = student.programme
        
        context = {
            'student': student,
            'programme': programme,
            'page_title': 'Student Dashboard',
        }
        
        return render(request, 'dashboards/student_dashboard.html', context)
    
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact administration.")
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
    


@login_required
def admin_dashboard(request):
    context = {
        'page_title': 'Admin Dashboard',
        'active_tab': 'dashboard',
        'user': request.user
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