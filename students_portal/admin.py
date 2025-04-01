from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'user_type', 'is_verified', 'status', 'created_at')
    list_filter = ('user_type', 'is_verified', 'status', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('user_type', 'is_verified', 'status', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'last_password_change')}),
        ('Security', {'fields': ('password_reset_token', 'password_reset_token_expiry')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'is_verified', 'status')
        }),
    )

class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('name',)

class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'faculty', 'description')
    search_fields = ('name', 'code')
    list_filter = ('faculty',)


class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'duration_years', 'semesters_per_year', 'description')
    search_fields = ('name', 'code')
    list_filter = ('department',)


class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'credit_hours', 'is_core', 'description')
    search_fields = ('name', 'code')
    list_filter = ('is_core',)

class ProgrammeUnitAdmin(admin.ModelAdmin):
    list_display = ('programme', 'unit', 'year_of_study', 'semester')
    search_fields = ('programme__name', 'unit__name', 'programme__code', 'unit__code')
    list_filter = ('year_of_study', 'semester', 'programme')


class LecturerAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'get_full_name', 'department', 'academic_rank', 'employment_type', 'status', 'is_active')
    search_fields = ('staff_id', 'first_name', 'last_name', 'middle_name', 'email', 'phone_number')
    list_filter = ('department', 'academic_rank', 'employment_type', 'status', 'is_active')
    readonly_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'



class StudentAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'get_full_name', 'programme', 'current_year', 'current_semester', 'status', 'is_active')
    search_fields = ('registration_number', 'first_name', 'last_name', 'middle_name', 'email', 'phone_number')
    list_filter = ('programme', 'current_year', 'current_semester', 'status', 'is_active', 'entry_mode')
    readonly_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'name', 'number', 'start_date', 'end_date', 'is_current')
    search_fields = ('academic_year__name', 'name', 'number')
    list_filter = ('academic_year', 'number', 'is_current')
    readonly_fields = ('start_date', 'end_date')



class UnitAllocationAdmin(admin.ModelAdmin):
    list_display = ('lecturer', 'programme_unit', 'semester')
    search_fields = ('lecturer__staff_id', 'programme_unit__unit__code', 'semester__academic_year__name')
    list_filter = ('semester', 'lecturer')

class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'programme_unit', 'semester')
    search_fields = ('student__registration_number', 'programme_unit__unit__code', 'semester__academic_year__name')
    list_filter = ('semester', 'programme_unit')

class AssessmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'weight_percentage')
    search_fields = ('name', 'code')

class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_allocation', 'assessment_type', 'date')
    search_fields = ('name', 'unit_allocation__programme_unit__unit__code')
    list_filter = ('assessment_type', 'unit_allocation')

class StudentScoreAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'assessment', 'score', 'submitted_date')
    search_fields = ('enrollment__student__registration_number', 'assessment__name')
    list_filter = ('assessment',)


class GradeSystemAdmin(admin.ModelAdmin):
    list_display = ('grade', 'min_score', 'max_score', 'points', 'description')
    search_fields = ('grade',)
    list_filter = ('grade',)


class StudentUnitGradeAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'total_score', 'grade', 'is_pass')
    search_fields = ('enrollment__student__registration_number', 'enrollment__programme_unit__unit__code')
    list_filter = ('grade', 'is_pass')


class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('unit_allocation', 'date', 'topic')
    search_fields = ('unit_allocation__programme_unit__unit__code', 'topic')
    list_filter = ('date', 'unit_allocation')


class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'attendance_record', 'is_present', 'remarks')
    search_fields = ('student__registration_number', 'attendance_record__date')
    list_filter = ('is_present', 'attendance_record__date')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'sender', 'created_at')
    search_fields = ('title', 'message', 'sender__username')
    list_filter = ('type', 'created_at')


class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification', 'is_read', 'read_at')
    search_fields = ('user__username', 'notification__title')
    list_filter = ('is_read', 'read_at')

class FeesStructureAdmin(admin.ModelAdmin):
    list_display = ('programme', 'academic_year', 'year_of_study', 'semester', 'amount')
    search_fields = ('programme__code', 'academic_year__name')
    list_filter = ('academic_year', 'year_of_study', 'semester')

class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'amount_paid', 'balance', 'last_payment_date')
    search_fields = ('student__registration_number',)
    list_filter = ('fee_structure',)

class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'student_fee', 'amount', 'payment_date', 'payment_method', 'recorded_by')
    search_fields = ('receipt_number', 'student_fee__student__registration_number')
    list_filter = ('payment_date', 'payment_method')




@admin.register(StudentReporting)
class StudentReportingAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_year', 'semester', 'reporting_status', 'reporting_date')
    list_filter = ('academic_year', 'semester', 'programme', 'reporting_status')
    search_fields = ('student__registration_number', 'student__first_name', 'student__last_name')

    
admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(FeesStructure, FeesStructureAdmin)
admin.site.register(StudentFee, StudentFeeAdmin)
admin.site.register(FeePayment, FeePaymentAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(StudentAttendance, StudentAttendanceAdmin)
admin.site.register(AttendanceRecord, AttendanceRecordAdmin)
admin.site.register(StudentUnitGrade, StudentUnitGradeAdmin)
admin.site.register(GradeSystem, GradeSystemAdmin)
admin.site.register(UnitAllocation, UnitAllocationAdmin)
admin.site.register(StudentEnrollment, StudentEnrollmentAdmin)
admin.site.register(AssessmentType, AssessmentTypeAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(StudentScore, StudentScoreAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Lecturer, LecturerAdmin)
admin.site.register(ProgrammeUnit, ProgrammeUnitAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(AcademicYear, AcademicYearAdmin)
admin.site.register(Faculty, FacultyAdmin)

