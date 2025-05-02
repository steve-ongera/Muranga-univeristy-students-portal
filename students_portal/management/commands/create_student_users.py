from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from students_portal.models import Student, User


class Command(BaseCommand):
    help = 'Create user accounts for all students with default password'

    def handle(self, *args, **kwargs):
        created_count = 0
        students = Student.objects.all()

        for student in students:
            reg_number = student.registration_number.strip().lower()

            if not User.objects.filter(username=reg_number).exists():
                User.objects.create_user(
                    username=reg_number,
                    first_name=student.first_name,
                    last_name=student.last_name,
                    email=student.email,
                    phone_number=student.phone_number,
                    user_type='student',
                    is_verified=True,
                    status='active',
                    password='12345678'
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created user for student: {reg_number}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Done. Total new student user accounts created: {created_count}"))
