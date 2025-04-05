from django import forms
from .models import *
from django.core.validators import RegexValidator

class StudentForm(forms.ModelForm):
    # Additional field customization
    email = forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'student@example.com'
    }),
    phone_number = forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '+254700000000'
    }),
    
    class Meta:
        model = Student
        fields = '__all__'
        widgets = {
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. ABC12345'
            }),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'programme': forms.Select(attrs={'class': 'form-select'}),
            'current_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_of_admission': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expected_graduation_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'email' : forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'student@example.com'
            }),
            'phone_number' : forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254700000000'
            }),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            'county': forms.TextInput(attrs={'class': 'form-control'}),
            'town': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'entry_mode': forms.Select(attrs={'class': 'form-select'}),
            'scholarship_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        help_texts = {
            'registration_number': 'Unique identifier for the student',
            'phone_number': 'Format: +254700000000',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields not required
        for field_name in ['middle_name', 'id_number', 'profile_picture', 
                         'expected_graduation_date', 'date_of_birth',
                         'religion', 'county', 'town', 'postal_address',
                         'postal_code', 'parent_name', 'parent_phone',
                         'emergency_contact_name', 'emergency_contact_relationship',
                         'emergency_contact_phone', 'scholarship_info']:
            self.fields[field_name].required = False


class LecturerForm(forms.ModelForm):
    # Additional field customization
    email = forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'student@example.com'
    }),
    phone_number = forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '+254700000000'
    }),

    class Meta:
        model = Lecturer
        fields = '__all__'
        widgets = {
            'staff_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. LEC12345'
            }),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_rank': forms.Select(attrs={'class': 'form-select'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'date_of_employment': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'lecturer@example.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254700000000'
            }),
            'biography': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'staff_id': 'Unique identifier for the lecturer',
            'phone_number': 'Format: +254700000000',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields not required
        for field_name in ['middle_name', 'national_id', 'qualification',
                         'specialization', 'academic_rank', 'date_of_employment',
                         'email', 'phone_number', 'biography', 'profile_picture']:
            self.fields[field_name].required = False



from django import forms
from .models import Student, Programme

class StudentSearchForm(forms.Form):
    """Form for searching students with various filter options"""
    registration_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registration Number'})
    )
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student Name'})
    )
    programme = forms.ModelChoiceField(
        queryset=Programme.objects.all(),
        required=False,
        empty_label="All Programmes",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    current_year = forms.ChoiceField(
        choices=[(0, 'All Years')] + [(i, f'Year {i}') for i in range(1, 5)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Student._meta.get_field('status').choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    entry_mode = forms.ChoiceField(
        choices=[('', 'All Entry Modes')] + Student._meta.get_field('entry_mode').choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    id_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID Number'})
    )



from django import forms
from .models import Student, Programme
from django.utils import timezone
from django.core.validators import RegexValidator

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'profile_picture',
            'registration_number',
            'first_name',
            'middle_name',
            'last_name',
            'id_number',
            'programme',
            'current_year',
            'current_semester',
            'date_of_admission',
            'date_of_birth',
            'gender',
            'email',
            'phone_number',
            'religion',
            'county',
            'town',
            'postal_address',
            'postal_code',
            'parent_name',
            'parent_phone',
            'emergency_contact_name',
            'emergency_contact_relationship',
            'emergency_contact_phone',
            'entry_mode',
            'scholarship_info'
        ]
        widgets = {
            'registration_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. ABC12345'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Middle Name (Optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'National ID/Passport'
            }),
            'programme': forms.Select(attrs={
                'class': 'form-select'
            }),
            'current_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 6
            }),
            'current_semester': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 3
            }),
            'date_of_admission': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'student@university.ac.ke'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+2547XXXXXXXX'
            }),
            'religion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Religion (Optional)'
            }),
            'county': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'County'
            }),
            'town': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Town/City'
            }),
            'postal_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'P.O. Box'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal Code'
            }),
            'parent_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Parent/Guardian's Full Name"
            }),
            'parent_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Parent/Guardian's Phone"
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Contact Name'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Relationship to Student'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Emergency Phone Number'
            }),
            'entry_mode': forms.Select(attrs={
                'class': 'form-select'
            }),
            'scholarship_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Scholarship details (if any)'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set current date as default for date fields if creating new student
        if not self.instance.pk:
            self.fields['date_of_admission'].initial = timezone.now().date()
        
        # Add form-control class to all fields automatically
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Basic phone number validation
            if not phone_number.startswith('+'):
                raise forms.ValidationError("Phone number should start with country code (e.g. +254)")
            if len(phone_number) < 10:
                raise forms.ValidationError("Phone number is too short")
        return phone_number

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob > timezone.now().date():
            raise forms.ValidationError("Date of birth cannot be in the future")
        return dob