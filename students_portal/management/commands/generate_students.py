import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from students_portal.models import Student, Programme

class Command(BaseCommand):
    help = 'Generate random student data'

    def handle(self, *args, **kwargs):
        first_names_male = ['John', 'Peter', 'Brian', 'Michael', 'David', 'James', 'Samuel', 'Joseph', 'Daniel', 'Ken']
        first_names_female = ['Mary', 'Jane', 'Alice', 'Lucy', 'Faith', 'Diana', 'Ann', 'Esther', 'Joan', 'Cynthia']
        last_names = ['Omondi', 'Mutua', 'Kamau', 'Odhiambo', 'Mwangi', 'Otieno', 'Chebet', 'Njoroge', 'Kiptoo', 'Wambui']
        towns = ['Nairobi', 'Kisumu', 'Nakuru', 'Eldoret', 'Meru', 'Thika', 'Kericho', 'Mombasa']
        counties = ['Nairobi', 'Kiambu', 'Muranga', 'Kisumu', 'Uasin Gishu', 'Mombasa', 'Embu', 'Machakos']
        parent_names = ['Paul Otieno', 'Susan Wanjiku', 'David Kiptoo', 'Jane Achieng', 'Robert Mwangi', 'Grace Chebet']

        date_of_admission = date(2024, 9, 3)

        programmes = list(Programme.objects.all())

        if not programmes:
            self.stdout.write(self.style.ERROR("No programmes found. Please add programmes first."))
            return

        existing_reg_numbers = set(Student.objects.values_list('registration_number', flat=True))

        for programme in programmes:
            num_students = random.randint(10, 16)

            for _ in range(num_students):
                gender = random.choice(['M', 'F'])
                first_name = random.choice(first_names_male if gender == 'M' else first_names_female)
                last_name = random.choice(last_names)
                middle_name = random.choice(first_names_male + first_names_female)

                # Ensure unique registration number
                for _ in range(1000):  # Avoid infinite loop
                    serial = random.randint(100, 999)
                    reg_number = f"{programme.code}/{serial}/2024"
                    if reg_number not in existing_reg_numbers:
                        existing_reg_numbers.add(reg_number)
                        break
                else:
                    self.stdout.write(self.style.ERROR(f"Could not generate unique reg_number for {programme.code}"))
                    continue

                id_number = str(random.randint(20000000, 39999999))
                dob = date(2004, 1, 1) + timedelta(days=random.randint(0, 2000))
                phone = f"07{random.randint(10000000, 99999999)}"
                email = f"{first_name.lower()}.{last_name.lower()}{random.randint(10,99)}@student.ac.ke"

                student = Student.objects.create(
                    registration_number=reg_number,
                    first_name=first_name,
                    last_name=last_name,
                    middle_name=middle_name,
                    id_number=id_number,
                    programme=programme,
                    current_year=1,
                    current_semester=1,
                    date_of_admission=date_of_admission,
                    expected_graduation_date=date(2028, 5, 31),
                    date_of_birth=dob,
                    gender=gender,
                    email=email,
                    phone_number=phone,
                    religion=random.choice(['Christianity', 'Islam', 'Atheist']),
                    county=random.choice(counties),
                    town=random.choice(towns),
                    postal_address=f"P.O BOX {random.randint(100, 9999)}",
                    postal_code=str(random.choice(['00100', '20100', '30100'])),
                    parent_name=random.choice(parent_names),
                    parent_phone=f"07{random.randint(10000000, 99999999)}",
                    emergency_contact_name=random.choice(parent_names),
                    emergency_contact_relationship='Parent',
                    emergency_contact_phone=f"07{random.randint(10000000, 99999999)}",
                    is_active=True,
                    status='active',
                    entry_mode=random.choice(['government_sponsored', 'self_sponsored']),
                )
                self.stdout.write(self.style.SUCCESS(f"Created {student.registration_number}"))
