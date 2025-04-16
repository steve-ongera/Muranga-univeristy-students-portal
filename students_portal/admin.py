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
    list_display = ('enrollment', 'total_score', 'grade', 'is_pass', 'get_academic_year')
    search_fields = ('enrollment__student__registration_number', 'enrollment__programme_unit__unit__code')
    list_filter = ('grade', 'is_pass', 'enrollment__semester__academic_year')

    def get_academic_year(self, obj):
        """Retrieve the academic year from enrollment"""
        return obj.enrollment.semester.academic_year.name  # Ensures retrieval from related models
    
    get_academic_year.short_description = 'Academic Year'  # Sets column title in admin panel



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

from django.contrib import admin
from django.utils.html import format_html
from .models import StudentComment, ClassSchedule, Announcement

@admin.register(StudentComment)
class StudentCommentAdmin(admin.ModelAdmin):
    list_display = ('student', 'truncated_comment', 'created_at', 'is_resolved', 'admin_action')
    list_filter = ('is_resolved', 'created_at', 'student__programme')
    search_fields = ('student__registration_number', 'student__first_name', 'student__last_name', 'comment')
    list_per_page = 20
    date_hierarchy = 'created_at'
    actions = ['mark_as_resolved', 'mark_as_unresolved']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student',)
        }),
        ('Comment Details', {
            'fields': ('comment', 'is_resolved')
        }),
        ('Admin Response', {
            'fields': ('admin_response', 'responded_by'),
            'classes': ('collapse',)
        }),
    )
    
    def truncated_comment(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    truncated_comment.short_description = 'Comment'
    
    def admin_action(self, obj):
        if obj.is_resolved:
            return format_html('<span style="color:green;">Resolved</span>')
        return format_html('<a href="/admin/your_app/studentcomment/{}/change/">Respond</a>', obj.id)
    admin_action.short_description = 'Action'
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True, responded_by=request.user)
    mark_as_resolved.short_description = "Mark selected comments as resolved"
    
    def mark_as_unresolved(self, request, queryset):
        queryset.update(is_resolved=False)
    mark_as_unresolved.short_description = "Mark selected comments as unresolved"
    
    def save_model(self, request, obj, form, change):
        if 'admin_response' in form.changed_data and not obj.responded_by:
            obj.responded_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'day_of_week', 'time_slot', 'venue', 'lecturer_name')
    list_filter = ('day_of_week', 'unit_allocation__semester', 'unit_allocation__lecturer')
    search_fields = ('unit_allocation__programme_unit__unit__name', 
                    'unit_allocation__programme_unit__unit__code',
                    'unit_allocation__lecturer__first_name',
                    'unit_allocation__lecturer__last_name')
    ordering = ('day_of_week', 'start_time')
    
    fieldsets = (
        ('Course Information', {
            'fields': ('unit_allocation',)
        }),
        ('Schedule Details', {
            'fields': ('day_of_week', ('start_time', 'end_time'), 'venue')
        }),
    )
    
    def course_name(self, obj):
        return obj.unit_allocation.programme_unit.unit.name
    course_name.short_description = 'Course'
    
    def lecturer_name(self, obj):
        return obj.unit_allocation.lecturer.get_full_name()
    lecturer_name.short_description = 'Lecturer'
    
    def time_slot(self, obj):
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}"
    time_slot.short_description = 'Time'

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'author', 'publish_date', 'is_recent')
    list_filter = ('department', 'publish_date', 'author')
    search_fields = ('title', 'content', 'department__name')
    date_hierarchy = 'publish_date'
    readonly_fields = ('author',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'department', 'publish_date')
        }),
        ('Content', {
            'fields': ('content',)
        }),
    )
    
    def is_recent(self, obj):
        return obj.publish_date >= timezone.now() - timezone.timedelta(days=7)
    is_recent.boolean = True
    is_recent.short_description = 'Recent?'
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

 # admin.py
from django.contrib import admin
from .models import QRAttendanceSession, QRAttendanceLog

@admin.register(QRAttendanceSession)
class QRAttendanceSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'unit_allocation',
        'lecturer',
        'qr_token',
        'valid_from',
        'valid_to',
        'latitude',
        'longitude',
        'max_distance_km',
    )
    search_fields = ('qr_token', 'lecturer__first_name', 'lecturer__last_name')
    list_filter = ('valid_from', 'valid_to')


@admin.register(QRAttendanceLog)
class QRAttendanceLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'session',
        'student',
        'scan_time',
        'device_fingerprint',
        'scan_latitude',
        'scan_longitude',
    )
    search_fields = ('student__registration_number', 'device_fingerprint')
    list_filter = ('scan_time', 'session__lecturer')

from django.contrib import admin
from .models import LectureHall, TimeSlot, Timetable, ScheduledLesson


@admin.register(LectureHall)
class LectureHallAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'building')
    list_filter = ('building',)
    search_fields = ('name', 'building', 'description')
    ordering = ('name',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('get_day_display', 'start_time', 'end_time')
    list_filter = ('day_of_week',)
    search_fields = ('start_time', 'end_time', 'day_of_week')  # Added search_fields
    ordering = ('day_of_week', 'start_time')
    
    def get_day_display(self, obj):
        return obj.get_day_of_week_display()
    get_day_display.short_description = 'Day'
    get_day_display.admin_order_field = 'day_of_week'


class ScheduledLessonInline(admin.TabularInline):
    model = ScheduledLesson
    extra = 1
    autocomplete_fields = ['unit_allocation', 'time_slot', 'lecture_hall']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('programme', 'year_of_study', 'semester', 'is_published', 'updated_at')
    list_filter = ('semester', 'programme', 'year_of_study', 'is_published')
    search_fields = ('programme__name', 'semester__name')
    inlines = [ScheduledLessonInline]
    list_editable = ('is_published',)
    actions = ['publish_timetables', 'unpublish_timetables']
    
    def publish_timetables(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} timetable(s) have been published.")
    publish_timetables.short_description = "Publish selected timetables"
    
    def unpublish_timetables(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} timetable(s) have been unpublished.")
    unpublish_timetables.short_description = "Unpublish selected timetables"


@admin.register(ScheduledLesson)
class ScheduledLessonAdmin(admin.ModelAdmin):
    list_display = ('get_unit_code', 'get_unit_name', 'time_slot', 'lecture_hall', 'frequency')
    list_filter = ('timetable__semester', 'timetable__programme', 'frequency', 'lecture_hall')
    search_fields = ('unit_allocation__programme_unit__unit__code', 'unit_allocation__programme_unit__unit__name', 'lecture_hall__name')
    autocomplete_fields = ['unit_allocation', 'time_slot', 'lecture_hall', 'timetable']
    
    def get_unit_code(self, obj):
        return obj.unit_allocation.programme_unit.unit.code
    get_unit_code.short_description = 'Unit Code'
    get_unit_code.admin_order_field = 'unit_allocation__programme_unit__unit__code'
    
    def get_unit_name(self, obj):
        return obj.unit_allocation.programme_unit.unit.name
    get_unit_name.short_description = 'Unit Name'
    get_unit_name.admin_order_field = 'unit_allocation__programme_unit__unit__name'

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

