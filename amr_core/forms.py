from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Patient, Antibiotic, ResistanceRecord, Prescription, 
    Feedback, Doctor, PatientAssessment, MedicineEffectivenessAlert,
    PatientMonitoringDashboard
)


class PatientForm(forms.ModelForm):
    """Form for adding/editing patient information"""
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'phone', 'email', 'medical_history', 'allergies']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter patient name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '150'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'medical_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter medical history (JSON format or free text)'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List any known allergies'
            }),
        }


class ResistanceRecordForm(forms.ModelForm):
    """Form for adding resistance records"""
    class Meta:
        model = ResistanceRecord
        fields = ['patient', 'antibiotic', 'result', 'test_date', 'test_method', 'notes']
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-select'
            }),
            'antibiotic': forms.Select(attrs={
                'class': 'form-select'
            }),
            'result': forms.Select(attrs={
                'class': 'form-select'
            }),
            'test_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'test_method': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MIC, Disk Diffusion'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about the resistance test'
            }),
        }


class PrescriptionForm(forms.ModelForm):
    """Form for creating prescriptions"""
    class Meta:
        model = Prescription
        fields = ['patient', 'antibiotic', 'diagnosis', 'dosage', 'frequency', 'duration', 'notes']
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_patient'
            }),
            'antibiotic': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_antibiotic'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter diagnosis details'
            }),
            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 500mg'
            }),
            'frequency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Twice daily'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 7 days'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional prescription notes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.doctor_name = kwargs.pop('doctor_name', None)
        super().__init__(*args, **kwargs)
        
        # Add custom validation
        self.fields['patient'].queryset = Patient.objects.all().order_by('name')
        self.fields['antibiotic'].queryset = Antibiotic.objects.all().order_by('name')


class FeedbackForm(forms.ModelForm):
    """Form for patient feedback"""
    class Meta:
        model = Feedback
        fields = ['feedback', 'details', 'severity_rating']
        widgets = {
            'feedback': forms.Select(attrs={
                'class': 'form-select'
            }),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please provide additional details about your experience'
            }),
            'severity_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'placeholder': 'Rate severity from 1-10 (optional)'
            }),
        }


class DoctorRegistrationForm(UserCreationForm):
    """Form for doctor registration"""
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your full name'
    }))
    license_number = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your medical license number'
    }))
    specialization = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your specialization'
    }))
    hospital = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your hospital/clinic name'
    }))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your phone number'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email address'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Doctor.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                license_number=self.cleaned_data['license_number'],
                specialization=self.cleaned_data.get('specialization', ''),
                hospital=self.cleaned_data.get('hospital', ''),
                phone=self.cleaned_data.get('phone', ''),
                email=self.cleaned_data.get('email', '')
            )
        return user


class LoginForm(forms.Form):
    """Simple login form"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }))


class PatientSearchForm(forms.Form):
    """Form for searching patients"""
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, phone, or email...'
        })
    )
    gender_filter = forms.ChoiceField(
        choices=[('', 'All Genders')] + Patient.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class AntibioticSearchForm(forms.Form):
    """Form for searching antibiotics"""
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name or bacteria...'
        })
    )
    class_filter = forms.ChoiceField(
        choices=[('', 'All Classes')] + Antibiotic.ANTIBIOTIC_CLASSES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )


class PrescriptionFilterForm(forms.Form):
    """Form for filtering prescriptions"""
    status_filter = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Prescription.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class PatientAssessmentForm(forms.ModelForm):
    """Form for patient assessment questionnaire"""
    class Meta:
        model = PatientAssessment
        fields = [
            'assessment_type', 'symptom_improvement', 'side_effects_experienced',
            'side_effects_details', 'medication_adherence', 'pain_level',
            'energy_level', 'appetite_changes', 'sleep_quality', 'additional_symptoms',
            'overall_satisfaction', 'doctor_notes', 'next_assessment_due'
        ]
        widgets = {
            'assessment_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'symptom_improvement': forms.Select(attrs={
                'class': 'form-select'
            }),
            'side_effects_experienced': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'side_effects_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe any side effects experienced...'
            }),
            'medication_adherence': forms.Select(attrs={
                'class': 'form-select'
            }),
            'pain_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'placeholder': 'Rate pain level 1-10'
            }),
            'energy_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'appetite_changes': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sleep_quality': forms.Select(attrs={
                'class': 'form-select'
            }),
            'additional_symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe any additional symptoms or concerns...'
            }),
            'overall_satisfaction': forms.Select(attrs={
                'class': 'form-select'
            }),
            'doctor_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Doctor notes and observations...'
            }),
            'next_assessment_due': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.doctor_name = kwargs.pop('doctor_name', None)
        super().__init__(*args, **kwargs)


class MedicineEffectivenessAlertForm(forms.ModelForm):
    """Form for creating medicine effectiveness alerts"""
    class Meta:
        model = MedicineEffectivenessAlert
        fields = [
            'alert_type', 'priority', 'title', 'description', 'triggered_by',
            'recommended_alternatives', 'alternative_reasoning', 'doctor_actions'
        ]
        widgets = {
            'alert_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alert title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detailed description of the alert...'
            }),
            'triggered_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'What triggered this alert?'
            }),
            'recommended_alternatives': forms.SelectMultiple(attrs={
                'class': 'form-select'
            }),
            'alternative_reasoning': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Reasoning for alternative recommendations...'
            }),
            'doctor_actions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Actions taken by doctor...'
            }),
        }


class PatientMonitoringForm(forms.ModelForm):
    """Form for patient monitoring dashboard"""
    class Meta:
        model = PatientMonitoringDashboard
        fields = [
            'treatment_start_date', 'expected_completion_date', 'treatment_status',
            'effectiveness_score', 'adherence_score', 'side_effects_score',
            'high_risk_factors', 'monitoring_notes', 'next_assessment_due'
        ]
        widgets = {
            'treatment_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expected_completion_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'treatment_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'effectiveness_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10',
                'step': '0.1'
            }),
            'adherence_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10',
                'step': '0.1'
            }),
            'side_effects_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10',
                'step': '0.1'
            }),
            'high_risk_factors': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List any high-risk factors...'
            }),
            'monitoring_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Monitoring notes and observations...'
            }),
            'next_assessment_due': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
