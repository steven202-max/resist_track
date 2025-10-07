from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class Patient(models.Model):
    """Patient model to store basic patient information"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True, help_text="JSON format or free text")
    allergies = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.age} years, {self.get_gender_display()})"
    
    def get_resistance_count(self):
        """Get count of resistant antibiotics for this patient"""
        return self.resistancerecord_set.filter(result='resistant').count()


class Antibiotic(models.Model):
    """Antibiotic model to store antibiotic information"""
    ANTIBIOTIC_CLASSES = [
        ('penicillin', 'Penicillin'),
        ('cephalosporin', 'Cephalosporin'),
        ('fluoroquinolone', 'Fluoroquinolone'),
        ('macrolide', 'Macrolide'),
        ('tetracycline', 'Tetracycline'),
        ('aminoglycoside', 'Aminoglycoside'),
        ('sulfonamide', 'Sulfonamide'),
        ('carbapenem', 'Carbapenem'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    bacteria_targeted = models.CharField(max_length=200, help_text="Comma-separated list of targeted bacteria")
    class_type = models.CharField(max_length=50, choices=ANTIBIOTIC_CLASSES)
    description = models.TextField(blank=True, null=True)
    dosage_info = models.TextField(blank=True, null=True, help_text="Standard dosage information")
    contraindications = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_class_type_display()})"
    
    def get_targeted_bacteria_list(self):
        """Return list of targeted bacteria"""
        return [b.strip() for b in self.bacteria_targeted.split(',') if b.strip()]
    
    def get_effectiveness_rate(self):
        """Calculate effectiveness rate based on feedback"""
        total_prescriptions = self.prescription_set.filter(status='completed').count()
        if total_prescriptions == 0:
            return 0
        
        recovered_count = self.prescription_set.filter(
            status='completed',
            feedback__feedback='recovered'
        ).count()
        
        return round((recovered_count / total_prescriptions) * 100, 1)


class ResistanceRecord(models.Model):
    """Model to track patient resistance to specific antibiotics"""
    RESISTANCE_CHOICES = [
        ('resistant', 'Resistant'),
        ('sensitive', 'Sensitive'),
        ('intermediate', 'Intermediate'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    antibiotic = models.ForeignKey(Antibiotic, on_delete=models.CASCADE)
    result = models.CharField(max_length=20, choices=RESISTANCE_CHOICES)
    test_date = models.DateField()
    test_method = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['patient', 'antibiotic']
        ordering = ['-test_date']
    
    def __str__(self):
        return f"{self.patient.name} - {self.antibiotic.name}: {self.result}"


class Prescription(models.Model):
    """Model to store prescriptions made by doctors"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    doctor_name = models.CharField(max_length=100)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    antibiotic = models.ForeignKey(Antibiotic, on_delete=models.CASCADE)
    diagnosis = models.TextField()
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100, help_text="e.g., '7 days', '2 weeks'")
    date_prescribed = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date_prescribed']
    
    def __str__(self):
        return f"{self.patient.name} - {self.antibiotic.name} ({self.status})"
    
    def is_patient_resistant(self):
        """Check if patient has resistance to this antibiotic"""
        resistance_record = ResistanceRecord.objects.filter(
            patient=self.patient,
            antibiotic=self.antibiotic,
            result='resistant'
        ).first()
        return resistance_record is not None
    
    def get_alternatives(self):
        """Get alternative antibiotics for the same bacteria"""
        if not self.antibiotic.bacteria_targeted:
            return Antibiotic.objects.none()
        
        targeted_bacteria = self.antibiotic.get_targeted_bacteria_list()
        alternatives = Antibiotic.objects.filter(
            bacteria_targeted__icontains=targeted_bacteria[0]  # Simple matching for demo
        ).exclude(id=self.antibiotic.id)
        
        # Filter out antibiotics the patient is resistant to
        resistant_antibiotic_ids = ResistanceRecord.objects.filter(
            patient=self.patient,
            result='resistant'
        ).values_list('antibiotic_id', flat=True)
        
        return alternatives.exclude(id__in=resistant_antibiotic_ids)


class Feedback(models.Model):
    """Model to store patient feedback on prescriptions"""
    FEEDBACK_CHOICES = [
        ('recovered', 'Recovered'),
        ('no_improvement', 'No Improvement'),
        ('side_effects', 'Side Effects'),
        ('worsening', 'Condition Worsening'),
        ('partial_recovery', 'Partial Recovery'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=20, choices=FEEDBACK_CHOICES)
    feedback_date = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True, help_text="Additional details about the feedback")
    severity_rating = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Severity rating from 1-10 (optional)"
    )
    
    class Meta:
        unique_together = ['patient', 'prescription']
        ordering = ['-feedback_date']
    
    def __str__(self):
        return f"{self.patient.name} - {self.prescription.antibiotic.name}: {self.get_feedback_display()}"


class Doctor(models.Model):
    """Extended doctor model (can be linked to User model)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    hospital = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"Dr. {self.name} ({self.license_number})"
    
    def get_total_prescriptions(self):
        """Get total prescriptions made by this doctor"""
        return Prescription.objects.filter(doctor_name=self.name).count()
    
    def get_prescriptions_by_status(self, status):
        """Get prescriptions by status"""
        return Prescription.objects.filter(doctor_name=self.name, status=status)


class AntibioticEffectiveness(models.Model):
    """Model to track overall antibiotic effectiveness statistics"""
    antibiotic = models.ForeignKey(Antibiotic, on_delete=models.CASCADE)
    bacteria_type = models.CharField(max_length=100)
    total_prescriptions = models.PositiveIntegerField(default=0)
    successful_treatments = models.PositiveIntegerField(default=0)
    failed_treatments = models.PositiveIntegerField(default=0)
    side_effects_reported = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['antibiotic', 'bacteria_type']
    
    def __str__(self):
        return f"{self.antibiotic.name} vs {self.bacteria_type}"
    
    def get_success_rate(self):
        """Calculate success rate percentage"""
        if self.total_prescriptions == 0:
            return 0
        return round((self.successful_treatments / self.total_prescriptions) * 100, 1)


class PatientAssessment(models.Model):
    """Model for patient assessment questionnaires"""
    ASSESSMENT_TYPE_CHOICES = [
        ('initial', 'Initial Assessment'),
        ('follow_up', 'Follow-up Assessment'),
        ('side_effects', 'Side Effects Assessment'),
        ('effectiveness', 'Effectiveness Assessment'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES)
    assessment_date = models.DateTimeField(auto_now_add=True)
    conducted_by = models.CharField(max_length=100, help_text="Doctor who conducted the assessment")
    
    # Assessment Questions and Responses
    symptom_improvement = models.CharField(max_length=20, choices=[
        ('significant', 'Significant Improvement'),
        ('moderate', 'Moderate Improvement'),
        ('minimal', 'Minimal Improvement'),
        ('no_change', 'No Change'),
        ('worsening', 'Condition Worsening'),
    ])
    
    side_effects_experienced = models.BooleanField(default=False)
    side_effects_details = models.TextField(blank=True, null=True)
    
    medication_adherence = models.CharField(max_length=20, choices=[
        ('excellent', 'Excellent - Taken as prescribed'),
        ('good', 'Good - Minor deviations'),
        ('fair', 'Fair - Some missed doses'),
        ('poor', 'Poor - Many missed doses'),
    ])
    
    pain_level = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Pain level from 1-10 (if applicable)"
    )
    
    energy_level = models.CharField(max_length=20, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ], blank=True, null=True)
    
    appetite_changes = models.CharField(max_length=20, choices=[
        ('improved', 'Improved'),
        ('same', 'Same'),
        ('decreased', 'Decreased'),
        ('lost', 'Lost appetite'),
    ], blank=True, null=True)
    
    sleep_quality = models.CharField(max_length=20, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ], blank=True, null=True)
    
    additional_symptoms = models.TextField(blank=True, null=True, help_text="Any new symptoms or concerns")
    
    overall_satisfaction = models.CharField(max_length=20, choices=[
        ('very_satisfied', 'Very Satisfied'),
        ('satisfied', 'Satisfied'),
        ('neutral', 'Neutral'),
        ('dissatisfied', 'Dissatisfied'),
        ('very_dissatisfied', 'Very Dissatisfied'),
    ])
    
    doctor_notes = models.TextField(blank=True, null=True)
    next_assessment_due = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ['-assessment_date']
    
    def __str__(self):
        return f"{self.patient.name} - {self.assessment_type} - {self.assessment_date.date()}"


class MedicineEffectivenessAlert(models.Model):
    """Model to track medicine effectiveness alerts and recommendations"""
    ALERT_TYPE_CHOICES = [
        ('ineffective', 'Medicine Ineffective'),
        ('side_effects', 'Severe Side Effects'),
        ('resistance', 'Antibiotic Resistance'),
        ('adherence', 'Poor Adherence'),
        ('interaction', 'Drug Interaction'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    title = models.CharField(max_length=200)
    description = models.TextField()
    triggered_by = models.CharField(max_length=100, help_text="What triggered this alert")
    created_date = models.DateTimeField(auto_now_add=True)
    acknowledged_by = models.CharField(max_length=100, blank=True, null=True)
    acknowledged_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ], default='active')
    
    # Alternative recommendations
    recommended_alternatives = models.ManyToManyField(Antibiotic, blank=True, related_name='recommended_for')
    alternative_reasoning = models.TextField(blank=True, null=True)
    
    # Doctor actions
    doctor_actions = models.TextField(blank=True, null=True, help_text="Actions taken by doctor")
    resolution_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_date', '-priority']
    
    def __str__(self):
        return f"{self.patient.name} - {self.alert_type} - {self.title}"


class PatientMonitoringDashboard(models.Model):
    """Model to track patient monitoring dashboard data"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    
    # Treatment Progress
    treatment_start_date = models.DateField()
    expected_completion_date = models.DateField()
    last_assessment_date = models.DateField(blank=True, null=True)
    next_assessment_due = models.DateField(blank=True, null=True)
    
    # Monitoring Status
    treatment_status = models.CharField(max_length=20, choices=[
        ('on_track', 'On Track'),
        ('monitoring', 'Requires Monitoring'),
        ('concern', 'Concern'),
        ('critical', 'Critical'),
        ('completed', 'Completed'),
    ], default='on_track')
    
    # Key Metrics
    effectiveness_score = models.FloatField(default=0.0, help_text="Overall effectiveness score 0-10")
    adherence_score = models.FloatField(default=0.0, help_text="Medication adherence score 0-10")
    side_effects_score = models.FloatField(default=0.0, help_text="Side effects severity score 0-10")
    
    # Risk Factors
    high_risk_factors = models.TextField(blank=True, null=True)
    monitoring_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['patient', 'prescription']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.patient.name} - {self.prescription.antibiotic.name} - {self.treatment_status}"
    
    def get_overall_risk_score(self):
        """Calculate overall risk score"""
        return round((self.side_effects_score + (10 - self.effectiveness_score) + (10 - self.adherence_score)) / 3, 1)