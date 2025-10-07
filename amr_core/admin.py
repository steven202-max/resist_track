from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Patient, Antibiotic, ResistanceRecord, Prescription, 
    Feedback, Doctor, AntibioticEffectiveness, PatientAssessment,
    MedicineEffectivenessAlert, PatientMonitoringDashboard
)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'gender', 'phone', 'resistance_count', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    def resistance_count(self, obj):
        count = obj.get_resistance_count()
        if count > 0:
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', count)
        return count
    resistance_count.short_description = 'Resistance Count'


@admin.register(Antibiotic)
class AntibioticAdmin(admin.ModelAdmin):
    list_display = ['name', 'class_type', 'bacteria_targeted', 'effectiveness_rate']
    list_filter = ['class_type', 'created_at']
    search_fields = ['name', 'bacteria_targeted', 'class_type']
    
    def effectiveness_rate(self, obj):
        rate = obj.get_effectiveness_rate()
        if rate >= 80:
            color = 'green'
        elif rate >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, rate)
    effectiveness_rate.short_description = 'Effectiveness Rate'


@admin.register(ResistanceRecord)
class ResistanceRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'antibiotic', 'result', 'test_date', 'test_method']
    list_filter = ['result', 'test_date', 'antibiotic__class_type']
    search_fields = ['patient__name', 'antibiotic__name']
    date_hierarchy = 'test_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'antibiotic')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'antibiotic', 'doctor_name', 'status', 'date_prescribed', 'resistance_alert']
    list_filter = ['status', 'date_prescribed', 'antibiotic__class_type']
    search_fields = ['patient__name', 'doctor_name', 'antibiotic__name']
    date_hierarchy = 'date_prescribed'
    readonly_fields = ['date_prescribed']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'antibiotic')
    
    def resistance_alert(self, obj):
        if obj.is_patient_resistant():
            return format_html('<span style="color: red; font-weight: bold;">⚠️ RESISTANT</span>')
        return format_html('<span style="color: green;">✓ Safe</span>')
    resistance_alert.short_description = 'Resistance Status'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['patient', 'prescription', 'feedback', 'feedback_date', 'severity_rating']
    list_filter = ['feedback', 'feedback_date']
    search_fields = ['patient__name', 'prescription__antibiotic__name']
    date_hierarchy = 'feedback_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'prescription')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'license_number', 'specialization', 'hospital', 'total_prescriptions']
    list_filter = ['specialization', 'hospital']
    search_fields = ['name', 'license_number', 'specialization']
    
    def total_prescriptions(self, obj):
        return obj.get_total_prescriptions()
    total_prescriptions.short_description = 'Total Prescriptions'


@admin.register(AntibioticEffectiveness)
class AntibioticEffectivenessAdmin(admin.ModelAdmin):
    list_display = ['antibiotic', 'bacteria_type', 'total_prescriptions', 'success_rate', 'last_updated']
    list_filter = ['bacteria_type', 'last_updated']
    search_fields = ['antibiotic__name', 'bacteria_type']
    readonly_fields = ['last_updated']
    
    def success_rate(self, obj):
        rate = obj.get_success_rate()
        if rate >= 80:
            color = 'green'
        elif rate >= 60:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, rate)
    success_rate.short_description = 'Success Rate'


@admin.register(PatientAssessment)
class PatientAssessmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'prescription', 'assessment_type', 'symptom_improvement', 'medication_adherence', 'assessment_date', 'conducted_by']
    list_filter = ['assessment_type', 'symptom_improvement', 'medication_adherence', 'assessment_date', 'conducted_by']
    search_fields = ['patient__name', 'prescription__antibiotic__name', 'conducted_by']
    readonly_fields = ['assessment_date']
    date_hierarchy = 'assessment_date'
    
    fieldsets = (
        ('Assessment Information', {
            'fields': ('patient', 'prescription', 'assessment_type', 'conducted_by', 'assessment_date')
        }),
        ('Patient Responses', {
            'fields': ('symptom_improvement', 'side_effects_experienced', 'side_effects_details', 'medication_adherence', 'pain_level', 'energy_level', 'appetite_changes', 'sleep_quality', 'additional_symptoms', 'overall_satisfaction')
        }),
        ('Doctor Notes', {
            'fields': ('doctor_notes', 'next_assessment_due')
        }),
    )


@admin.register(MedicineEffectivenessAlert)
class MedicineEffectivenessAlertAdmin(admin.ModelAdmin):
    list_display = ['patient', 'prescription', 'alert_type', 'priority_display', 'title', 'status', 'created_date']
    list_filter = ['alert_type', 'priority', 'status', 'created_date']
    search_fields = ['patient__name', 'prescription__antibiotic__name', 'title', 'description']
    readonly_fields = ['created_date']
    date_hierarchy = 'created_date'
    
    def priority_display(self, obj):
        priority_colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        color = priority_colors.get(obj.priority, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_priority_display())
    priority_display.short_description = 'Priority'
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('patient', 'prescription', 'alert_type', 'priority', 'title', 'description', 'triggered_by', 'created_date')
        }),
        ('Status & Actions', {
            'fields': ('status', 'acknowledged_by', 'acknowledged_date', 'doctor_actions', 'resolution_notes')
        }),
        ('Recommendations', {
            'fields': ('recommended_alternatives', 'alternative_reasoning')
        }),
    )


@admin.register(PatientMonitoringDashboard)
class PatientMonitoringDashboardAdmin(admin.ModelAdmin):
    list_display = ['patient', 'prescription', 'treatment_status_display', 'effectiveness_score', 'adherence_score', 'side_effects_score', 'risk_score_display', 'updated_at']
    list_filter = ['treatment_status', 'updated_at']
    search_fields = ['patient__name', 'prescription__antibiotic__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def treatment_status_display(self, obj):
        status_colors = {
            'on_track': 'green',
            'monitoring': 'orange',
            'concern': 'red',
            'critical': 'darkred',
            'completed': 'blue'
        }
        color = status_colors.get(obj.treatment_status, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_treatment_status_display())
    treatment_status_display.short_description = 'Status'
    
    def risk_score_display(self, obj):
        risk_score = obj.get_overall_risk_score()
        if risk_score <= 3:
            color = 'green'
        elif risk_score <= 6:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{:.1f}</span>', color, risk_score)
    risk_score_display.short_description = 'Risk Score'
    
    fieldsets = (
        ('Patient & Treatment', {
            'fields': ('patient', 'prescription', 'treatment_start_date', 'expected_completion_date', 'treatment_status')
        }),
        ('Monitoring Scores', {
            'fields': ('effectiveness_score', 'adherence_score', 'side_effects_score')
        }),
        ('Assessment Schedule', {
            'fields': ('last_assessment_date', 'next_assessment_due')
        }),
        ('Risk Factors & Notes', {
            'fields': ('high_risk_factors', 'monitoring_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )