from django.core.management.base import BaseCommand
from students_portal.models import Student, User

class Command(BaseCommand):
    help = 'Create user accounts for students who do not already have one'

    def handle(self, *args, **kwargs):
        created_count = 0
        students = Student.objects.all()

        for student in students:
            username = student.registration_number.strip().lower()

            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    first_name=student.first_name,
                    last_name=student.last_name,
                    email=student.email,
                    phone_number=student.phone_number,
                    user_type='student',
                    is_verified=True,
                    status='active',
                    password='cp7kvt'  # Default password
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created user account for: {username}"))

        if created_count:
            self.stdout.write(self.style.SUCCESS(f"\n🎉 Successfully created {created_count} new student user accounts."))
        else:
            self.stdout.write(self.style.WARNING("ℹ️ All students already have user accounts."))
