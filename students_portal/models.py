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
    is_special = models.BooleanField(default=False)

    current_week = models.PositiveSmallIntegerField(
        default=1,
        
    )
    
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
            self.is_pass = total_score >= 40  # You can set the pass mark as per the university's rule (e.g., >= 50%)
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

    # ... existing fields ...
    week_number = models.IntegerField(blank=True, null=True)  # Week 1 through 10
    is_locked = models.BooleanField(default=False)  # To prevent changes after submission
    
    class Meta:
        unique_together = ('unit_allocation', 'week_number')
    
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


class StudentComment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True, null=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='responded_comments')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Student Comment'
        verbose_name_plural = 'Student Comments'
    
    def __str__(self):
        return f"Comment by {self.student.registration_number} on {self.created_at.date()}"
    

# In models.py
class ClassSchedule(models.Model):
    unit_allocation = models.ForeignKey(UnitAllocation, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            # If you need weekends:
            # (5, 'Saturday'),
            # (6, 'Sunday')
        ],
        help_text="Day of the week (0=Monday, 1=Tuesday, ..., 4=Friday)"
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100)
    
class Announcement(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    publish_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-publish_date']


from django.db import models
from django.utils import timezone

class LectureNotes(models.Model):
    unit_allocation = models.ForeignKey(
        'UnitAllocation', 
        on_delete=models.CASCADE,
        related_name='lecture_notes'
    )
    topic = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='lecture_notes/')
    date_uploaded = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_uploaded']
        verbose_name_plural = "Lecture Notes"

    def __str__(self):
        return f"{self.topic} - {self.unit_allocation.programme_unit.unit.code}"
    

    # models.py
# models.py
from django.db import models

class QRAttendanceSession(models.Model):
    """Temporary QR code sessions without GIS"""
    unit_allocation = models.ForeignKey(UnitAllocation, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    qr_token = models.CharField(max_length=255, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)  # Instead of PointField
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    max_distance_km = models.DecimalField(max_digits=5, decimal_places=2, default=0.05)  # 50m = 0.05km

class QRAttendanceLog(models.Model):
    """Track QR scans without GIS"""
    session = models.ForeignKey(QRAttendanceSession, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    scan_time = models.DateTimeField(auto_now_add=True)
    device_fingerprint = models.CharField(max_length=64)
    scan_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    scan_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    
    class Meta:
        unique_together = [('session', 'student'), ('session', 'device_fingerprint')]


#Time table management 
class LectureHall(models.Model):
    """Model for lecture halls/rooms"""
    name = models.CharField(max_length=50, unique=True)  # e.g., ML1, ML2
    capacity = models.IntegerField()
    building = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    """Model for time slots (e.g., 8:00-10:00)"""
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])
    
    class Meta:
        unique_together = ('start_time', 'end_time', 'day_of_week')
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"


class Timetable(models.Model):
    """Model to represent a timetable for a semester"""
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='timetables')
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='timetables')
    year_of_study = models.IntegerField()  # 1, 2 , etc.
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('semester', 'programme', 'year_of_study')
    
    def __str__(self):
        return f"{self.programme.name} Year {self.year_of_study} - {self.semester}"


class ScheduledLesson(models.Model):
    """Model for scheduled unit lessons"""
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='scheduled_lessons')
    unit_allocation = models.ForeignKey(UnitAllocation, on_delete=models.CASCADE, related_name='scheduled_lessons')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.PROTECT, related_name='scheduled_lessons')
    lecture_hall = models.ForeignKey(LectureHall, on_delete=models.PROTECT, related_name='scheduled_lessons')
    frequency = models.CharField(max_length=20, choices=[
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('custom', 'Custom Schedule'),
    ], default='weekly')
    
    class Meta:
        unique_together = ('timetable', 'time_slot', 'lecture_hall')
    
    def __str__(self):
        return f"{self.unit_allocation.programme_unit.unit.code} at {self.time_slot} in {self.lecture_hall}"


# models.py
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
import secrets
from datetime import timedelta

class SpecialExamApplication(models.Model):
    """Model to track special/supplementary exam applications"""
    APPLICATION_TYPES = (
        ('supplementary', 'Supplementary Exam'),
        ('special', 'Special Exam'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('paid', 'Payment Complete'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_applications')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    application_date = models.DateTimeField(auto_now_add=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_reference = models.CharField(max_length=50, blank=True, null=True)
    verification_code = models.CharField(max_length=12, unique=True)
    code_expiry = models.DateTimeField()
    admin_remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-application_date']
    
    def __str__(self):
        return f"{self.student.registration_number} - {self.get_application_type_display()} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
            self.code_expiry = timezone.now() + timedelta(days=7)  # Code expires in 7 days
        super().save(*args, **kwargs)
    
    def generate_verification_code(self):
        return secrets.token_hex(6).upper()  # 12-character hex code
    
    def is_code_valid(self):
        return timezone.now() < self.code_expiry
    
    def calculate_payment_amount(self, units_count):
        # KSH 800 per supplementary exam
        return units_count * 800


class AppliedExamUnit(models.Model):
    """Units included in an exam application"""
    application = models.ForeignKey(SpecialExamApplication, on_delete=models.CASCADE, related_name='applied_units')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    original_enrollment = models.ForeignKey(StudentEnrollment, on_delete=models.CASCADE)
    original_grade = models.ForeignKey(StudentUnitGrade, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('application', 'unit')
    
    def __str__(self):
        return f"{self.application} - {self.unit.code}"



class Hostel(models.Model):
    """Model for university hostels"""
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    
    name = models.CharField(max_length=100)  # Kilimanjaro, Mount Kenya, etc.
    code = models.CharField(max_length=10, unique=True)  # e.g., HOST-KILI
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    capacity = models.PositiveIntegerField(default=1600)  # 400 rooms × 4 beds
    current_occupancy = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    warden_name = models.CharField(max_length=100, blank=True)
    warden_contact = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"

class Room(models.Model):
    """Model for individual rooms in hostels"""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)  # e.g., "A101"
    capacity = models.PositiveIntegerField(default=4)
    current_occupancy = models.PositiveIntegerField(default=0)
    is_full = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('hostel', 'room_number')
    
    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"

class Bed(models.Model):
    """Model for individual beds within rooms"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=5)  # e.g., "Bed1", "Bed2"
    is_occupied = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('room', 'bed_number')
    
    def __str__(self):
        return f"{self.room} - {self.bed_number}"
    


class HostelAllocation(models.Model):
    """Tracks student hostel assignments per academic year"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hostel_allocations')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE)
    date_allocated = models.DateField(auto_now_add=True)
    date_vacated = models.DateField( null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = (
            ('student', 'academic_year'),  # 1 student per year
            ('bed', 'academic_year'),     # 1 student per bed per year
        )
    
    def __str__(self):
        return f"{self.student} - {self.hostel} ({self.academic_year})"
    

from django.utils import timezone

class DiscussionGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(default=timezone.now)
    is_public = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class GroupMember(models.Model):
    group = models.ForeignKey(DiscussionGroup, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    joined_at = models.DateTimeField(default=timezone.now)
    is_admin = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('group', 'user')
    
    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class GroupMessage(models.Model):
    group = models.ForeignKey(DiscussionGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username} in {self.group.name}: {self.content[:50]}"




class NewsArticle(models.Model):
    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('event', 'Events'),
        ('announcement', 'Announcements'),
        ('sports', 'Sports'),
        ('general', 'General'),
    ]
    
    title = models.CharField(max_length=200)
    summary = models.TextField()
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    publish_date = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-publish_date']
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'



class StudentClub(models.Model):
    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
        ('religious', 'Religious'),
        ('social', 'Social'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    chairperson = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='chaired_clubs')
    contact_phone = models.CharField(max_length=15)
    email = models.EmailField()
    meeting_schedule = models.TextField()
    membership_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    logo = models.ImageField(upload_to='club_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class ClubMembership(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='club_memberships')
    club = models.ForeignKey(StudentClub, on_delete=models.CASCADE, related_name='members')
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_executive = models.BooleanField(default=False)
    position = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        unique_together = ('student', 'club')
    
    def __str__(self):
        return f"{self.student.username} in {self.club.name}"





class ClubEvent(models.Model):
    EVENT_STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    club = models.ForeignKey(StudentClub, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=100)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='organized_events')
    status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='upcoming')
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    registration_required = models.BooleanField(default=False)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_datetime']
        
    def __str__(self):
        return f"{self.title} - {self.club.name}"
    
    def save(self, *args, **kwargs):
        # Automatically update status based on current time
        now = timezone.now()
        if self.start_datetime > now:
            self.status = 'upcoming'
        elif self.start_datetime <= now <= self.end_datetime:
            self.status = 'ongoing'
        elif self.end_datetime < now:
            self.status = 'completed'
        super().save(*args, **kwargs)