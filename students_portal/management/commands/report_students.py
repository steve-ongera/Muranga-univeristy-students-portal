import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from students_portal.models import Student, AcademicYear, Semester, StudentReporting

class Command(BaseCommand):
    help = "Generate reporting records for students for 5 academic years (semesters 1 and 2 only)."

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        created_count = 0
        skipped_count = 0

        students = Student.objects.all()
        academic_years = AcademicYear.objects.order_by('start_date')

        if not academic_years.exists():
            self.stdout.write(self.style.ERROR("No academic years found."))
            return

        for student in students:
            admitted_date = student.date_of_admission
            admitted_year = None

            # Find the academic year the student was admitted in
            for ay in academic_years:
                if ay.start_date <= admitted_date <= ay.end_date:
                    admitted_year = ay
                    break

            if not admitted_year:
                self.stdout.write(self.style.WARNING(f"⏭️  Skipping student {student.registration_number} - admission date not within known academic years"))
                continue

            admitted_index = list(academic_years).index(admitted_year)
            target_years = academic_years[admitted_index:admitted_index + 5]

            for year in target_years:
                # Determine semesters based on programme
                sems = Semester.objects.filter(academic_year=year).order_by('number')
                sem_count = student.programme.semesters_per_year  # Assumes Programme model has this field
                sems = sems[:sem_count]  # Get only sem 1 and 2 or 3

                for sem in sems:
                    if sem.number > 2:
                        continue  # Only Sem 1 and 2

                    # Skip if already exists
                    if StudentReporting.objects.filter(student=student, academic_year=year, semester=sem).exists():
                        skipped_count += 1
                        continue

                    reporting_date = year.start_date + timedelta(days=random.randint(5, 9))

                    StudentReporting.objects.create(
                        student=student,
                        academic_year=year,
                        programme=student.programme,
                        semester=sem,
                        reporting_status='reported',
                        reporting_date=reporting_date,
                        is_fees_cleared=random.choice([True, False])
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ Reported: {student.registration_number} - AY {year} Sem {sem.number}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Done! {created_count} reporting records created."))
        if skipped_count:
            self.stdout.write(self.style.WARNING(f"ℹ️ {skipped_count} existing records were skipped."))
