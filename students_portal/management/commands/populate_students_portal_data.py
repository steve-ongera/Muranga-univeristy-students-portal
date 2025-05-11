from django.core.management.base import BaseCommand
from students_portal.models import CommonQuestion, QuickLink
from django.db import transaction

class Command(BaseCommand):
    help = 'Populates database with initial Muranga University student portal data'

    def handle(self, *args, **options):
        # Copy the questions and links data from the script
        # Then add the population code

        

        # First, clear existing data to avoid duplicates
        print("Clearing existing data...")
        CommonQuestion.objects.all().delete()
        QuickLink.objects.all().delete()

        # List of common questions specific to Muranga University students
        questions = [
            {
                "question": "How do I access my student portal?",
                "answer": "To access your student portal, visit portal.mrua.ac.ke and log in with your student ID and password provided during registration.",
                "order": 1
            },
            {
                "question": "When are the fee payment deadlines?",
                "answer": "Fee payment deadlines are: Semester 1 - September 15th, Semester 2 - January 15th, and Semester 3 - May 15th. Late payments incur a penalty of Ksh 1,000.",
                "order": 2
            },
            {
                "question": "How do I register for courses this semester?",
                "answer": "Course registration is done online through the student portal. Log in, select 'Course Registration' and follow the prompts. Registration period is typically two weeks before semester start.",
                "order": 3
            },
            {
                "question": "Where can I find my exam timetable?",
                "answer": "Exam timetables are posted on the student portal under 'Examinations' section and on department notice boards three weeks before exam period begins.",
                "order": 4
            },
            {
                "question": "How do I apply for accommodation in university hostels?",
                "answer": "Hostel applications are done through the student portal under 'Accommodation'. The application window opens two months before semester begins. First-come, first-served basis.",
                "order": 5
            },
            {
                "question": "What are the library opening hours?",
                "answer": "The main library is open from 8:00 AM to 10:00 PM on weekdays, 9:00 AM to 5:00 PM on Saturdays, and 12:00 PM to 5:00 PM on Sundays.",
                "order": 6
            },
            {
                "question": "How do I join student clubs and societies?",
                "answer": "Visit the Student Affairs office or attend the clubs fair during orientation week. Most clubs also have sign-up forms on their social media pages or the student portal.",
                "order": 7
            },
            {
                "question": "What is the procedure for deferring a semester?",
                "answer": "To defer a semester, fill the deferral form available at the Registrar's office or student portal. Submit it with supporting documents at least two weeks before semester starts.",
                "order": 8
            },
            {
                "question": "How do I access my academic transcript?",
                "answer": "Official transcripts can be requested from the Examinations Office with a fee of Ksh 1,000. Allow 3-5 working days for processing. Unofficial transcripts are available on your student portal.",
                "order": 9
            },
            {
                "question": "What is the process for appealing exam results?",
                "answer": "To appeal exam results, fill an examination remarking form from your department within two weeks after results release. There's a non-refundable fee of Ksh 2,500 per unit.",
                "order": 10
            },
            {
                "question": "How can I contact my academic advisor?",
                "answer": "Academic advisors' contact information is available on the departmental website and notice boards. You can also find your assigned advisor in the student portal under 'Academic Support'.",
                "order": 11
            },
            {
                "question": "When is the next graduation ceremony?",
                "answer": "The annual graduation ceremony is held in December. Exact dates are announced three months prior through university emails and notice boards.",
                "order": 12
            },
            {
                "question": "Where can I find internship opportunities?",
                "answer": "Internship opportunities are posted on the Career Services portal, departmental notice boards, and through the Industrial Attachment Office located at the Main Administration Block.",
                "order": 13
            },
            {
                "question": "How do I access the university Wi-Fi?",
                "answer": "Connect to 'MRUA_STUDENT' network and log in using your student portal credentials. If you face issues, visit the ICT Helpdesk at the Library basement.",
                "order": 14
            },
            {
                "question": "What mental health services are available for students?",
                "answer": "The Student Counseling Center offers free counseling services on weekdays from 8:00 AM to 5:00 PM. You can book appointments through the student portal or visit their office at the Student Center.",
                "order": 15
            },
            {
                "question": "How do I apply for financial aid or scholarships?",
                "answer": "Financial aid applications are done through the Financial Aid Office or student portal under 'Scholarships & Aid'. Application deadlines are typically announced at the beginning of each academic year.",
                "order": 16
            },
            {
                "question": "What sports facilities are available on campus?",
                "answer": "Muranga University offers a gym, football field, basketball court, volleyball court, and swimming pool. Access is free for all registered students with a valid student ID.",
                "order": 17
            },
            {
                "question": "How do I report a complaint or grievance?",
                "answer": "Complaints can be submitted through the student portal under 'Student Services > Complaints', or by visiting the Dean of Students office. Anonymous reporting is available for sensitive issues.",
                "order": 18
            },
            {
                "question": "What are the semester start and end dates?",
                "answer": "For the current academic year: Semester 1 (Sep - Dec), Semester 2 (Jan - Apr), and Semester 3 (May - Aug). Exact dates are available on the academic calendar on the university website.",
                "order": 19
            },
            {
                "question": "How do I get my student ID card replaced if lost?",
                "answer": "Visit the Registrar's office with Ksh 1,000 replacement fee receipt from the Finance office. Bring a passport photo and allow 3-5 working days for processing.",
                "order": 20
            }
        ]

        # List of quick links specific to Muranga University
        links = [
            {
                "title": "Student Portal Login",
                "url": "https://portal.mrua.ac.ke",
                "icon": "bi-person-circle",
                "order": 1
            },
            {
                "title": "E-Learning Platform",
                "url": "https://elearning.mrua.ac.ke",
                "icon": "bi-book",
                "order": 2
            },
            {
                "title": "Fee Payment",
                "url": "https://payments.mrua.ac.ke",
                "icon": "bi-credit-card",
                "order": 3
            },
            {
                "title": "Academic Calendar",
                "url": "https://www.mrua.ac.ke/calendar",
                "icon": "bi-calendar-event",
                "order": 4
            },
            {
                "title": "Library Resources",
                "url": "https://library.mrua.ac.ke",
                "icon": "bi-journal-richtext",
                "order": 5
            },
            {
                "title": "Career Services",
                "url": "https://careers.mrua.ac.ke",
                "icon": "bi-briefcase",
                "order": 6
            },
            {
                "title": "University Email",
                "url": "https://mail.mrua.ac.ke",
                "icon": "bi-envelope",
                "order": 7
            },
            {
                "title": "Campus Map",
                "url": "https://www.mrua.ac.ke/map",
                "icon": "bi-geo-alt",
                "order": 8
            }
        ]

        # Use transaction to ensure all or nothing is saved
        with transaction.atomic():
            # Create all common questions
            print("Adding common questions...")
            for q_data in questions:
                CommonQuestion.objects.create(**q_data)
                print(f"Added question: {q_data['question']}")
            
            # Create all quick links
            print("Adding quick links...")
            for link_data in links:
                QuickLink.objects.create(**link_data)
                print(f"Added link: {link_data['title']}")

        print("\nData population complete!")
        print(f"Added {len(questions)} questions and {len(links)} quick links to the database.")

        self.stdout.write(self.style.SUCCESS('Successfully populated portal data'))

