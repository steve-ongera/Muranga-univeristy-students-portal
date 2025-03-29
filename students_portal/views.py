from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *


def login_view(request):
    """
    Handle login for both students and lecturers.
    Username should be either registration_number (for students) or staff_id (for lecturers).
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate with Django's auth system
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Determine if the user is a student or lecturer
            try:
                student = Student.objects.get(registration_number=username)
                # Set session variable to indicate this is a student
                request.session['user_type'] = 'student'
                request.session['student_id'] = student.id
                return redirect('student_dashboard')
            except Student.DoesNotExist:
                try:
                    lecturer = Lecturer.objects.get(staff_id=username)
                    # Set session variable to indicate this is a lecturer
                    request.session['user_type'] = 'lecturer'
                    request.session['lecturer_id'] = lecturer.id
                    return redirect('lecturer_dashboard')
                except Lecturer.DoesNotExist:
                    # User exists but not associated with student or lecturer - unusual case
                    messages.error(request, "User account exists but is not linked to a student or lecturer profile.")
                    return redirect('login')
        else:
            # Authentication failed - now try to find if username exists as reg_number or staff_id
            is_student = Student.objects.filter(registration_number=username).exists()
            is_lecturer = Lecturer.objects.filter(staff_id=username).exists()
            
            if is_student or is_lecturer:
                messages.error(request, "Invalid password. Please try again.")
            else:
                messages.error(request, "Invalid username. No student or lecturer found with this ID.")
            
            return render(request, 'login.html', {'username': username})
    
    # If GET request, just show the login form
    return render(request, 'auth/login.html')


def registration_view(request):
    """
    Handle user registration for both students and lecturers.
    Username should be either registration_number (for students) or staff_id (for lecturers).
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')  # 'student' or 'lecturer'
        
        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'auth/registration.html', {'username': username, 'user_type': user_type})
        
        # Validate username exists in appropriate model
        if user_type == 'student':
            try:
                student = Student.objects.get(registration_number=username)
                full_name = student.get_full_name()
                
                # Check if user already exists 
                if User.objects.filter(username=username).exists():
                    messages.error(request, "A user with this registration number already exists.")
                    return render(request, 'auth/registration.html', {'username': username, 'user_type': user_type})
                
                # Create new user
                user = User.objects.create_user(username=username, password=password)
                user.first_name = student.first_name
                user.last_name = student.last_name
                user.email = student.email or ''
                user.save()
                
                messages.success(request, f"Student account created successfully for {full_name}.")
                return redirect('login')
                
            except Student.DoesNotExist:
                messages.error(request, "No student found with this registration number.")
                return render(request, 'auth/registration.html', {'username': username, 'user_type': user_type})
                
        elif user_type == 'lecturer':
            try:
                lecturer = Lecturer.objects.get(staff_id=username)
                full_name = lecturer.get_full_name()
                
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    messages.error(request, "A user with this staff ID already exists.")
                    return render(request, 'auth/registration.html', {'username': username, 'user_type': user_type})
                
                # Create new user
                user = User.objects.create_user(username=username, password=password)
                user.first_name = lecturer.first_name
                user.last_name = lecturer.last_name
                user.email = lecturer.email or ''
                user.save()
                
                messages.success(request, f"Lecturer account created successfully for {full_name}.")
                return redirect('login')
                
            except Lecturer.DoesNotExist:
                messages.error(request, "No lecturer found with this staff ID.")
                return render(request, 'auth/registration.html', {'username': username, 'user_type': user_type})
        
        else:
            messages.error(request, "Invalid user type selected.")
            return render(request, 'auth/registration.html', {'username': username})
    
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