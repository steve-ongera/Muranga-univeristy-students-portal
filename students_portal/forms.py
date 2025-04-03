from django import forms
from .models import *
from django.core.validators import RegexValidator

class StudentForm(forms.ModelForm):
    # Additional field customization
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    email = forms.EmailField(required=False)
    
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
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'student@example.com'
            }),
            'phone_number': forms.TextInput(attrs={
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
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    email = forms.EmailField(required=False)

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