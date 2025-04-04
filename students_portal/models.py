from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """Extended user model for authentication"""
    USER_TYPES = (
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('admin', 'Administrator'),
        ('staff', 'Administrative Staff'),
        ('finance', 'Finance Officer'),
    )
    
    # User type and status
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ], default='active')
    
    # Contact information
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Security
    last_password_change = models.DateTimeField(default=timezone.now)
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_token_expiry = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"


class AcademicYear(models.Model):
    """Model for academic year"""
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class Faculty(models.Model):
    """Model for faculties/schools in the university"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """Model for departments within faculties"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class Programme(models.Model):
    """Model for academic programmes/courses"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programmes')
    duration_years = models.IntegerField()
    semesters_per_year = models.IntegerField(default=2)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Unit(models.Model):
    """Model for course units/subjects"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    credit_hours = models.IntegerField(default=3)
    is_core = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ProgrammeUnit(models.Model):
    """Model for mapping units to programmes and specific years/semesters"""
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='programme_units')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='programme_units')
    year_of_study = models.IntegerField()
    semester = models.IntegerField()
    
    class Meta:
        unique_together = ('programme', 'unit', 'year_of_study', 'semester')
    
    def __str__(self):
        return f"{self.programme.code} - {self.unit.code} (Y{self.year_of_study}, S{self.semester})"


class Lecturer(models.Model):
    """Model for lecturers"""
    # Basic identification fields
    staff_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    
    
    # Academic and professional information
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='lecturers')
    qualification = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    academic_rank = models.CharField(max_length=50, choices=[
        ('professor', 'Professor'),
        ('associate_professor', 'Associate Professor'),
        ('senior_lecturer', 'Senior Lecturer'),
        ('lecturer', 'Lecturer'),
        ('assistant_lecturer', 'Assistant Lecturer'),
        ('tutorial_fellow', 'Tutorial Fellow'),
        ('graduate_assistant', 'Graduate Assistant'),
    ], blank=True, null=True)
    
    # Employment details
    employment_type = models.CharField(max_length=50, choices=[
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('visiting', 'Visiting'),
        ('adjunct', 'Adjunct'),
    ], default='full_time')
    date_of_employment = models.DateField(blank=True, null=True)
    
   
    
    # Contact information
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    
    # Additional information
    biography = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='lecturer_profiles/', blank=True, null=True)
    
    # System status
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('sabbatical', 'Sabbatical'),
        ('terminated', 'Terminated'),
        ('retired', 'Retired'),
    ], default='active')
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_full_name(self):
        """Return the lecturer's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.staff_id} - {self.get_full_name()}"


class Student(models.Model):
    """Model for students"""
    # Basic identification fields
    registration_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    id_number = models.CharField(max_length=20, blank=True, null=True)
    
    profile_picture = models.ImageField(upload_to='lecturer_profiles/', blank=True, null=True)
    
    # Academic information
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='students')
    current_year = models.IntegerField()
    current_semester = models.IntegerField()
    date_of_admission = models.DateField()
    expected_graduation_date = models.DateField(blank=True, null=True)
    
    # Personal information
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ], blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Address information
    religion = models.CharField(max_length=50, blank=True, null=True)
    county = models.CharField(max_length=50, blank=True, null=True)
    town = models.CharField(max_length=50, blank=True, null=True)
    postal_address = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    # Parents contact
    parent_name = models.CharField(max_length=100, blank=True, null=True)
    parent_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Academic status
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('deferred', 'Deferred'),
        ('suspended', 'Suspended'),
        ('transferred', 'Transferred'),
        ('withdrawn', 'Withdrawn')
    ], default='active')
    
    # Additional academic info
    entry_mode = models.CharField(max_length=20, choices=[
        ('government_sponsored', 'Government-Sponsored'),
        ('self_sponsored', 'Self-Sponsored'),
        ('parallel', 'Parallel'),
        ('exchange', 'Exchange'),
        ('transfer', 'Transfer')
    ], default='government_sponsored')
    scholarship_info = models.TextField(blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_full_name(self):
        """Return the student's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.registration_number} - {self.get_full_name()}"


class Semester(models.Model):
    """Model for semesters within academic years"""
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    name = models.CharField(max_length=50)
    number = models.IntegerField()  # 1, 2, or 3 depending on programme
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('academic_year', 'number')
    
    def __str__(self):
        return f"{self.academic_year.name} - Semester {self.number}"


class UnitAllocation(models.Model):
    """Model for allocating units to lecturers in specific semesters"""
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE, related_name='unit_allocations')
    programme_unit = models.ForeignKey(ProgrammeUnit, on_delete=models.CASCADE, related_name='unit_allocations')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='unit_allocations')
    
    class Meta:
        unique_together = ('lecturer', 'programme_unit', 'semester')
    
    def __str__(self):
        return f"{self.lecturer.staff_id} - {self.programme_unit.unit.code} ({self.semester})"


class StudentEnrollment(models.Model):
    """Model for student enrollment in units for specific semesters"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    programme_unit = models.ForeignKey(ProgrammeUnit, on_delete=models.CASCADE, related_name='enrollments')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='enrollments')
    
    class Meta:
        unique_together = ('student', 'programme_unit', 'semester')
    
    def __str__(self):
        return f"{self.student.registration_number} - {self.programme_unit.unit.code}"


class AssessmentType(models.Model):
    """Model for different types of assessments (CAT, Final Exam, etc.)"""
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} ({self.weight_percentage}%)"


class Assessment(models.Model):
    """Model for specific assessment instances"""
    unit_allocation = models.ForeignKey(UnitAllocation, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE, related_name='assessments')
    name = models.CharField(max_length=100)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    date = models.DateField()
    
    def __str__(self):
        return f"{self.name} - {self.unit_allocation.programme_unit.unit.code}"


class StudentScore(models.Model):
    """Model for student scores in assessments"""
    enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE, related_name='scores')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='scores')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    submitted_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('enrollment', 'assessment')
    
    def __str__(self):
        return f"{self.enrollment.student.registration_number} - {self.assessment.name} - {self.score}"


from django.db import models

class GradeSystem(models.Model):
    """Model for grade system (A, B, C, D, E, F)"""
    grade = models.CharField(max_length=2)
    min_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    points = models.DecimalField(max_digits=3, decimal_places=1)
    description = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.grade} ({self.min_score} - {self.max_score})"


class StudentUnitGrade(models.Model):
    """Model for final unit grades for students"""
    enrollment = models.OneToOneField(StudentEnrollment, on_delete=models.CASCADE, related_name='final_grade')
    cat_average = models.DecimalField(max_digits=5, decimal_places=2)
    exam_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.ForeignKey(GradeSystem, on_delete=models.PROTECT, related_name='student_grades', null=True, blank=True)
    is_pass = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.enrollment.student.registration_number} - {self.enrollment.programme_unit.unit.code} - {self.grade.grade if self.grade else 'Pending'}"

    def calculate_total_score(self):
        """Automatically calculate total score (CAT + Exam Score)"""
        return self.cat_average + self.exam_score

    def assign_grade_and_pass_status(self):
        """Assign grade and pass status based on total score"""
        total_score = self.calculate_total_score()
        self.total_score = total_score

        # Get the grade from the GradeSystem based on the total score
        grade = GradeSystem.objects.filter(min_score__lte=total_score, max_score__gte=total_score).first()

        if grade:
            self.grade = grade
            self.is_pass = total_score >= 50  # You can set the pass mark as per the university's rule (e.g., >= 50%)
        else:
            self.grade = None
            self.is_pass = False

    def save(self, *args, **kwargs):
        """Override save method to automatically calculate and assign grade and pass status"""
        self.assign_grade_and_pass_status()
        super().save(*args, **kwargs)


class AttendanceRecord(models.Model):
    """Model for tracking student attendance"""
    unit_allocation = models.ForeignKey(UnitAllocation, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    topic = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.unit_allocation.programme_unit.unit.code} - {self.date}"


class StudentAttendance(models.Model):
    """Model for individual student attendance"""
    attendance_record = models.ForeignKey(AttendanceRecord, on_delete=models.CASCADE, related_name='student_attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    is_present = models.BooleanField(default=False)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        unique_together = ('attendance_record', 'student')
    
    def __str__(self):
        return f"{self.student.registration_number} - {self.attendance_record.date} - {'Present' if self.is_present else 'Absent'}"


class Notification(models.Model):
    """Model for system notifications"""
    NOTIFICATION_TYPES = (
        ('announcement', 'Announcement'),
        ('grade', 'Grade Release'),
        ('exam', 'Exam Schedule'),
        ('fee', 'Fee Reminder'),
        ('registration', 'Registration'),
        ('other', 'Other'),
    )
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    
    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"


class UserNotification(models.Model):
    """Model for notifications directed to specific users"""
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='user_notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.notification.title}"


class FeesStructure(models.Model):
    """Model for fee structures"""
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='fee_structures')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='fee_structures')
    year_of_study = models.IntegerField()
    semester = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('programme', 'academic_year', 'year_of_study', 'semester')
    
    def __str__(self):
        return f"{self.programme.code} - Year {self.year_of_study} - Sem {self.semester} - {self.academic_year.name}"


class StudentFee(models.Model):
    """Model for tracking student fee payments"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_records')
    fee_structure = models.ForeignKey(FeesStructure, on_delete=models.CASCADE, related_name='student_fees')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    last_payment_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.student.registration_number} - {self.fee_structure} - Balance: {self.balance}"


class FeePayment(models.Model):
    """Model for individual fee payments"""
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    receipt_number = models.CharField(max_length=50, unique=True)
    payment_method = models.CharField(max_length=50)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_payments')
    
    def __str__(self):
        return f"{self.receipt_number} - {self.student_fee.student.registration_number} - {self.amount}"



from django.db import models
from django.utils import timezone

class StudentReporting(models.Model):
    """
    Model to track student reporting by academic year, programme, and semester.
    Helps administrators know how many students have reported in each period.
    """
    REPORTING_STATUS = (
        ('reported', 'Reported'),
        ('not_reported', 'Not Reported'),
        ('deferred', 'Deferred'),
        ('on_leave', 'On Leave'),
    )

    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name='reporting_records',
        verbose_name='Student'
    )
    academic_year = models.ForeignKey(
        'AcademicYear',
        on_delete=models.CASCADE,
        related_name='student_reportings',
        verbose_name='Academic Year'
    )
    programme = models.ForeignKey(
        'Programme',
        on_delete=models.CASCADE,
        related_name='reporting_records',
        verbose_name='Programme'
    )
    semester = models.ForeignKey(
        'Semester',
        on_delete=models.CASCADE,
        related_name='student_reportings',
        verbose_name='Semester'
    )
    reporting_status = models.CharField(
        max_length=20,
        choices=REPORTING_STATUS,
        default='not_reported',
        verbose_name='Reporting Status'
    )
    reporting_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Reporting Date'
    )
    is_fees_cleared = models.BooleanField(
        default=False,
        verbose_name='Fees Cleared'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Administrative Notes'
    )

    class Meta:
        verbose_name = 'Student Reporting'
        verbose_name_plural = 'Student Reporting Records'
        unique_together = ('student', 'academic_year', 'semester')
        ordering = ['-academic_year__start_date', '-semester__number']

    def __str__(self):
        return f"{self.student.registration_number} - {self.academic_year} - Sem {self.semester.number} - {self.get_reporting_status_display()}"

    def save(self, *args, **kwargs):
        """Update reporting date when status changes to 'reported'"""
        if self.reporting_status == 'reported' and not self.reporting_date:
            self.reporting_date = timezone.now().date()
        super().save(*args, **kwargs)