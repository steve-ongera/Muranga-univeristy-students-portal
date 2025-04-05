# Muranga University of Technology - University Management System

## Overview
The Muranga University of Technology Management System is a comprehensive Django-based web application designed to modernize and streamline administrative operations, academic processes, and student services. This custom-built platform integrates seamlessly with existing university infrastructure while providing a user-friendly experience for administrators, faculty, and students.

## Core Features

### Admin Management Portal
- **User Management**: Centralized control for managing students, faculty, and administrative staff accounts
- **Department & Faculty Administration**: Structure management, staff allocation, and resource distribution
- **Academic Program Management**: Creation and configuration of programs, courses, and curriculum
- **Financial Oversight**: Fee structure management, payment tracking, and financial reporting
- **System Configuration**: Academic calendar setup, grading systems, and institutional parameters
- **Comprehensive Reporting**: Custom reports for enrollment, performance, attendance, and more
- **Announcement System**: Campus-wide communication system with targeted messaging options

### Faculty Dashboard
- **Course Management**: Course materials, syllabus, and resource management
- **Student Assessment**: Grading interface with automatic calculation and grade submission
- **Attendance Tracking**: Digital attendance recording with automated reports
- **Student Performance Analytics**: Visual representation of class and individual performance
- **Communication Tools**: Direct messaging with students and student groups
- **Exam Management**: Scheduling, invigilation assignments, and results processing
- **Office Hours**: Scheduling system with automatic student notifications

### Student Portal
- **Course Registration**: Intuitive interface for course selection and registration
- **Academic Records**: Complete academic history with semester-wise breakdown
- **Grade Access**: Secure viewing of grades with GPA calculation
- **Timetable Generation**: Personalized class schedules with calendar integration
- **Fee Management**: Payment history, invoices, and online payment options
- **Document Repository**: Access to lecture notes, assignments, and supplementary materials
- **Communication Center**: Direct messaging with instructors and administrative departments
- **Exam Information**: Schedules, venues, and results
- **Digital ID**: Integrated student identification system
- **Student Services**: Access to library services, accommodation, and campus resources

## Technical Specifications

### Technology Stack
- **Framework**: Django 4.2+ (Python 3.9+)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: PostgreSQL 14+
- **Authentication**: Django Authentication System with custom extensions
- **Caching**: Redis
- **Task Queue**: Celery for background processing
- **APIs**: Django REST Framework for mobile integration
- **Deployment**: Docker, Nginx, Gunicorn
- **File Storage**: AWS S3 compatible storage
- **Monitoring**: Prometheus & Grafana

### System Architecture
- Modular design following Django's MVT (Model-View-Template) architecture
- Microservices approach for scalable components
- RESTful API design for frontend-backend communication
- Responsive design for cross-device compatibility
- Optimized database queries for handling large student datasets

## Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 14+
- Redis 6+
- Git

### Development Environment Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/murangauniversity/ums.git
   cd ums
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with appropriate database credentials and other configuration.

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Load initial data:
   ```bash
   python manage.py loaddata initial_data
   ```

8. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Production Deployment
Detailed production deployment instructions are available in the `docs/deployment.md` file, covering:
- Server provisioning
- Docker configuration
- Database optimization
- SSL setup
- Load balancing
- Backup strategies

## Project Structure
```
muranga_ums/
├── account/                 # User authentication and profiles
├── academics/               # Academic programs and curriculum
├── administration/          # Administrative functions
├── api/                     # REST API endpoints
├── config/                  # Project configuration
├── core/                    # Core functionality and shared components
├── dashboard/               # Dashboard interfaces
├── docs/                    # Documentation
├── faculty/                 # Faculty-specific modules
├── finance/                 # Financial management
├── media/                   # User-uploaded files
├── static/                  # Static assets
├── student/                 # Student-specific modules
├── templates/               # HTML templates
├── utils/                   # Utility functions
├── manage.py
├── requirements.txt
└── docker-compose.yml
```

## Customization for Muranga University of Technology
- Branded interface with university colors, logo, and style guidelines
- Custom academic structure reflecting Muranga University's specific departments and faculties
- Integration capabilities with existing university systems
- Localized features specific to Kenyan higher education requirements
- Compliance with Commission for University Education (CUE) standards
- Custom reporting aligned with institutional and governmental requirements

## Data Security & Compliance
- Role-based access control with granular permissions
- Data encryption at rest and in transit
- Comprehensive audit logging
- GDPR-compliant data handling
- Regular automated backups
- Two-factor authentication for sensitive operations

## Support & Maintenance
- 12-month technical support included
- Comprehensive documentation for administrators and users
- Video tutorials for common operations
- Regular software updates and security patches
- Training sessions for administrative staff

## Licensing
This software is provided exclusively to Muranga University of Technology under the terms specified in the accompanying license agreement. Unauthorized reproduction or distribution is prohibited.

## Contact Information
For technical support or inquiries:
- Email: support@murangaums.ac.ke
- Phone: +254 112284093
- Support Portal: https://support.murangaums.ac.ke

---

© 2025 Muranga University of Technology. All rights reserved.