from django import template
from ..models import AttendanceRecord

register = template.Library()

@register.filter
def get_week(records, week):
    """Filter to get attendance record for specific week"""
    try:
        week_num = int(week)
        return next((r for r in records if r.week_number == week_num), None)
    except (ValueError, StopIteration):
        return None

@register.filter
def get_student_attendance(record, student_id):
    """Filter to get student's attendance status for a record"""
    if not record:
        return {'is_present': False, 'remarks': ''}
    try:
        return record.student_attendances.get(student_id=student_id)
    except:
        return {'is_present': False, 'remarks': ''}

@register.filter
def count_present(record):
    """Count present students for a record"""
    if not record:
        return 0
    return record.student_attendances.filter(is_present=True).count()


from django import template

register = template.Library()

@register.filter
def has_signed_current_week(enrollment, current_week):
    """Check if student has signed attendance for current week"""
    unit = enrollment.programme_unit.unit_allocation
    return unit.attendance_records.filter(
        week_number=current_week,
        student_attendances__student_id=enrollment.student_id
    ).exists()

@register.filter
def multiply(value, arg):
    """Multiply value by arg for progress bar calculation"""
    return value * arg

from django import template
from ..models import AttendanceRecord, StudentAttendance

# Create the register variable
register = template.Library()

@register.filter
def has_signed_current_week(enrollment, args):
    """Check if student has signed attendance for current week"""
    try:
        current_week, unit_allocation_id = args.split(',')
        return AttendanceRecord.objects.filter(
            unit_allocation_id=unit_allocation_id,
            week_number=int(current_week),
            student_attendances__student_id=enrollment.student_id
        ).exists()
    except:
        return False

@register.filter
def multiply(value, arg):
    """Multiply value by arg for progress bar calculation"""
    try:
        return int(value) * int(arg)
    except:
        return 0
    