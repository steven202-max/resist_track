from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    Patient, Antibiotic, ResistanceRecord, Prescription, 
    Feedback, Doctor, AntibioticEffectiveness, PatientAssessment,
    MedicineEffectivenessAlert, PatientMonitoringDashboard
)
from .forms import (
    PatientForm, ResistanceRecordForm, PrescriptionForm, FeedbackForm,
    DoctorRegistrationForm, LoginForm, PatientSearchForm, 
    AntibioticSearchForm, PrescriptionFilterForm, PatientAssessmentForm,
    MedicineEffectivenessAlertForm, PatientMonitoringForm
)


def home(request):
    """Home page with system overview"""
    context = {
        'total_patients': Patient.objects.count(),
        'total_antibiotics': Antibiotic.objects.count(),
        'active_prescriptions': Prescription.objects.filter(status='active').count(),
        'resistance_records': ResistanceRecord.objects.count(),
    }
    return render(request, 'amr_core/home.html', context)


def doctor_login(request):
    """Doctor login page"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, Dr. {user.get_full_name() or user.username}!')
                return redirect('doctor_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'amr_core/doctor_login.html', {'form': form})


def doctor_register(request):
    """Doctor registration page"""
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('doctor_login')
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'amr_core/doctor_register.html', {'form': form})


@login_required
def doctor_dashboard(request):
    """Doctor dashboard with key metrics and actions"""
    # Get doctor's information
    try:
        doctor = Doctor.objects.get(user=request.user)
        doctor_name = doctor.name
    except Doctor.DoesNotExist:
        doctor_name = request.user.username
    
    # Get recent prescriptions by this doctor
    recent_prescriptions = Prescription.objects.filter(
        doctor_name__icontains=doctor_name
    ).order_by('-date_prescribed')[:10]
    
    # Get resistance alerts
    resistance_alerts = []
    for prescription in recent_prescriptions:
        if prescription.is_patient_resistant():
            resistance_alerts.append(prescription)
    
    # Get statistics
    total_prescriptions = Prescription.objects.filter(doctor_name__icontains=doctor_name).count()
    active_prescriptions = Prescription.objects.filter(
        doctor_name__icontains=doctor_name, 
        status='active'
    ).count()
    
    context = {
        'doctor_name': doctor_name,
        'recent_prescriptions': recent_prescriptions,
        'resistance_alerts': resistance_alerts,
        'total_prescriptions': total_prescriptions,
        'active_prescriptions': active_prescriptions,
    }
    
    return render(request, 'amr_core/doctor_dashboard.html', context)


@login_required
def add_patient(request):
    """Add new patient"""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient added successfully!')
            return redirect('patient_list')
    else:
        form = PatientForm()
    
    return render(request, 'amr_core/add_patient.html', {'form': form})


@login_required
def patient_list(request):
    """List all patients with search functionality"""
    search_form = PatientSearchForm(request.GET)
    patients = Patient.objects.all()
    
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search_query')
        gender_filter = search_form.cleaned_data.get('gender_filter')
        
        if search_query:
            patients = patients.filter(
                Q(name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        if gender_filter:
            patients = patients.filter(gender=gender_filter)
    
    paginator = Paginator(patients, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    
    return render(request, 'amr_core/patient_list.html', context)


@login_required
def patient_detail(request, patient_id):
    """View patient details with resistance history"""
    patient = get_object_or_404(Patient, id=patient_id)
    resistance_records = ResistanceRecord.objects.filter(patient=patient).order_by('-test_date')
    prescriptions = Prescription.objects.filter(patient=patient).order_by('-date_prescribed')
    
    context = {
        'patient': patient,
        'resistance_records': resistance_records,
        'prescriptions': prescriptions,
    }
    
    return render(request, 'amr_core/patient_detail.html', context)


@login_required
def prescribe_antibiotic(request):
    """Prescribe antibiotic with resistance checking"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        doctor_name = doctor.name
    except Doctor.DoesNotExist:
        doctor_name = request.user.username
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, doctor_name=doctor_name)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor_name = doctor_name
            prescription.save()
            
            # Check for resistance
            if prescription.is_patient_resistant():
                messages.warning(request, 
                    f'⚠️ WARNING: {prescription.patient.name} has resistance to {prescription.antibiotic.name}!')
                return redirect('prescription_alternatives', prescription_id=prescription.id)
            else:
                messages.success(request, 
                    f'✅ Prescription created successfully! '
                    f'Patient ID: {prescription.patient.id}, '
                    f'Prescription ID: {prescription.id}')
                return redirect('prescription_success', prescription_id=prescription.id)
    else:
        form = PrescriptionForm(doctor_name=doctor_name)
    
    return render(request, 'amr_core/prescribe_antibiotic.html', {'form': form})


@login_required
def prescription_success(request, prescription_id):
    """Show prescription success page with patient and prescription IDs"""
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    context = {
        'prescription': prescription,
    }
    
    return render(request, 'amr_core/prescription_success.html', context)


@login_required
def prescription_alternatives(request, prescription_id):
    """Show alternative antibiotics for resistant prescriptions"""
    prescription = get_object_or_404(Prescription, id=prescription_id)
    alternatives = prescription.get_alternatives()
    
    if request.method == 'POST':
        # Update prescription with alternative antibiotic
        alternative_id = request.POST.get('alternative_antibiotic')
        if alternative_id:
            alternative = get_object_or_404(Antibiotic, id=alternative_id)
            prescription.antibiotic = alternative
            prescription.save()
            messages.success(request, f'Prescription updated to {alternative.name}')
            return redirect('doctor_dashboard')
    
    context = {
        'prescription': prescription,
        'alternatives': alternatives,
    }
    
    return render(request, 'amr_core/prescription_alternatives.html', context)


def patient_feedback(request):
    """Patient feedback form (no login required)"""
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        prescription_id = request.POST.get('prescription_id')
        
        if patient_id and prescription_id:
            try:
                patient = Patient.objects.get(id=patient_id)
                prescription = Prescription.objects.get(id=prescription_id, patient=patient)
                
                # Check if feedback already exists
                existing_feedback = Feedback.objects.filter(
                    patient=patient, 
                    prescription=prescription
                ).first()
                
                if existing_feedback:
                    form = FeedbackForm(request.POST, instance=existing_feedback)
                else:
                    form = FeedbackForm(request.POST)
                
                if form.is_valid():
                    feedback = form.save(commit=False)
                    feedback.patient = patient
                    feedback.prescription = prescription
                    feedback.save()
                    
                    # Update prescription status if feedback indicates completion
                    if feedback.feedback in ['recovered', 'side_effects']:
                        prescription.status = 'completed'
                        prescription.save()
                    
                    messages.success(request, 'Thank you for your feedback!')
                    return redirect('patient_feedback')
                else:
                    messages.error(request, 'Please check your input and try again.')
            except (Patient.DoesNotExist, Prescription.DoesNotExist):
                messages.error(request, 'Invalid patient or prescription ID.')
        else:
            messages.error(request, 'Please provide both patient and prescription IDs.')
    
    # Show form for entering IDs
    return render(request, 'amr_core/patient_feedback.html')


def feedback_form(request):
    """Show feedback form after patient enters IDs"""
    patient_id = request.GET.get('patient_id')
    prescription_id = request.GET.get('prescription_id')
    
    if not patient_id or not prescription_id:
        messages.error(request, 'Missing required parameters.')
        return redirect('patient_feedback')
    
    try:
        patient = Patient.objects.get(id=patient_id)
        prescription = Prescription.objects.get(id=prescription_id, patient=patient)
        
        # Check if feedback already exists
        existing_feedback = Feedback.objects.filter(
            patient=patient, 
            prescription=prescription
        ).first()
        
        if existing_feedback:
            form = FeedbackForm(instance=existing_feedback)
            is_update = True
        else:
            form = FeedbackForm()
            is_update = False
        
        context = {
            'patient': patient,
            'prescription': prescription,
            'form': form,
            'is_update': is_update,
        }
        
        return render(request, 'amr_core/feedback_form.html', context)
        
    except (Patient.DoesNotExist, Prescription.DoesNotExist):
        messages.error(request, 'Invalid patient or prescription ID.')
        return redirect('patient_feedback')


@login_required
def add_resistance_record(request):
    """Add resistance record for a patient"""
    if request.method == 'POST':
        form = ResistanceRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resistance record added successfully!')
            return redirect('resistance_records')
    else:
        form = ResistanceRecordForm()
    
    return render(request, 'amr_core/add_resistance_record.html', {'form': form})


@login_required
def resistance_records(request):
    """List all resistance records"""
    records = ResistanceRecord.objects.select_related('patient', 'antibiotic').order_by('-test_date')
    
    paginator = Paginator(records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'amr_core/resistance_records.html', context)


@login_required
def reports(request):
    """Reports and analytics dashboard"""
    # Antibiotic effectiveness data
    antibiotics = Antibiotic.objects.all()
    antibiotic_data = []
    
    for antibiotic in antibiotics:
        total_prescriptions = Prescription.objects.filter(antibiotic=antibiotic).count()
        recovered_count = Feedback.objects.filter(
            prescription__antibiotic=antibiotic,
            feedback='recovered'
        ).count()
        
        if total_prescriptions > 0:
            effectiveness_rate = round((recovered_count / total_prescriptions) * 100, 1)
        else:
            effectiveness_rate = 0
        
        antibiotic_data.append({
            'name': antibiotic.name,
            'class_type': antibiotic.class_type,
            'total_prescriptions': total_prescriptions,
            'recovered_count': recovered_count,
            'effectiveness_rate': effectiveness_rate,
        })
    
    # Resistance statistics
    resistance_stats = ResistanceRecord.objects.values('result').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent feedback
    recent_feedback = Feedback.objects.select_related(
        'patient', 'prescription__antibiotic'
    ).order_by('-feedback_date')[:10]
    
    context = {
        'antibiotic_data': antibiotic_data,
        'resistance_stats': resistance_stats,
        'recent_feedback': recent_feedback,
    }
    
    return render(request, 'amr_core/reports.html', context)


@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def check_resistance_ajax(request):
    """AJAX endpoint to check resistance in real-time"""
    if request.method == 'GET':
        patient_id = request.GET.get('patient_id')
        antibiotic_id = request.GET.get('antibiotic_id')
        
        if patient_id and antibiotic_id:
            try:
                resistance_record = ResistanceRecord.objects.get(
                    patient_id=patient_id,
                    antibiotic_id=antibiotic_id,
                    result='resistant'
                )
                return JsonResponse({
                    'is_resistant': True,
                    'message': f'Patient is resistant to this antibiotic (tested on {resistance_record.test_date})',
                    'test_date': resistance_record.test_date.strftime('%Y-%m-%d'),
                    'test_method': resistance_record.test_method or 'Not specified'
                })
            except ResistanceRecord.DoesNotExist:
                return JsonResponse({
                    'is_resistant': False,
                    'message': 'No resistance detected'
                })
    
    return JsonResponse({'error': 'Invalid parameters'})


def get_alternatives_ajax(request):
    """AJAX endpoint to get alternative antibiotics"""
    if request.method == 'GET':
        patient_id = request.GET.get('patient_id')
        antibiotic_id = request.GET.get('antibiotic_id')
        
        if patient_id and antibiotic_id:
            try:
                prescription = Prescription(
                    patient_id=patient_id,
                    antibiotic_id=antibiotic_id
                )
                alternatives = prescription.get_alternatives()
                
                alternatives_data = []
                for alt in alternatives:
                    alternatives_data.append({
                        'id': alt.id,
                        'name': alt.name,
                        'class_type': alt.class_type,
                        'bacteria_targeted': alt.bacteria_targeted,
                        'effectiveness_rate': alt.get_effectiveness_rate()
                    })
                
                return JsonResponse({
                    'alternatives': alternatives_data
                })
            except Exception as e:
                return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Invalid parameters'})


@login_required
def patient_dashboard(request, patient_id):
    """Patient monitoring dashboard"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    # Get patient's active prescriptions
    active_prescriptions = Prescription.objects.filter(
        patient=patient, status='active'
    ).order_by('-date_prescribed')
    
    # Get monitoring dashboards for active prescriptions
    monitoring_dashboards = PatientMonitoringDashboard.objects.filter(
        patient=patient,
        prescription__status='active'
    ).order_by('-updated_at')
    
    # Get recent assessments
    recent_assessments = PatientAssessment.objects.filter(
        patient=patient
    ).order_by('-assessment_date')[:5]
    
    # Get active alerts
    active_alerts = MedicineEffectivenessAlert.objects.filter(
        patient=patient,
        status='active'
    ).order_by('-created_date')[:10]
    
    # Get recent feedback
    recent_feedback = Feedback.objects.filter(
        patient=patient
    ).order_by('-feedback_date')[:5]
    
    context = {
        'patient': patient,
        'active_prescriptions': active_prescriptions,
        'monitoring_dashboards': monitoring_dashboards,
        'recent_assessments': recent_assessments,
        'active_alerts': active_alerts,
        'recent_feedback': recent_feedback,
    }
    
    return render(request, 'amr_core/patient_dashboard.html', context)


@login_required
def patient_assessment(request, patient_id, prescription_id=None):
    """Patient assessment form"""
    patient = get_object_or_404(Patient, id=patient_id)
    
    if prescription_id:
        prescription = get_object_or_404(Prescription, id=prescription_id, patient=patient)
    else:
        # Get the most recent active prescription
        prescription = Prescription.objects.filter(
            patient=patient, status='active'
        ).order_by('-date_prescribed').first()
    
    try:
        doctor = Doctor.objects.get(user=request.user)
        doctor_name = doctor.name
    except Doctor.DoesNotExist:
        doctor_name = request.user.username
    
    if request.method == 'POST':
        form = PatientAssessmentForm(request.POST, doctor_name=doctor_name)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.patient = patient
            assessment.prescription = prescription
            assessment.conducted_by = doctor_name
            assessment.save()
            
            # Update monitoring dashboard
            monitoring_dashboard, created = PatientMonitoringDashboard.objects.get_or_create(
                patient=patient,
                prescription=prescription,
                defaults={
                    'treatment_start_date': prescription.date_prescribed.date(),
                    'expected_completion_date': prescription.date_prescribed.date() + timedelta(days=7),
                }
            )
            
            # Update scores based on assessment
            if assessment.symptom_improvement == 'significant':
                monitoring_dashboard.effectiveness_score = 9.0
            elif assessment.symptom_improvement == 'moderate':
                monitoring_dashboard.effectiveness_score = 7.0
            elif assessment.symptom_improvement == 'minimal':
                monitoring_dashboard.effectiveness_score = 5.0
            elif assessment.symptom_improvement == 'no_change':
                monitoring_dashboard.effectiveness_score = 3.0
            else:
                monitoring_dashboard.effectiveness_score = 1.0
            
            # Update adherence score
            if assessment.medication_adherence == 'excellent':
                monitoring_dashboard.adherence_score = 10.0
            elif assessment.medication_adherence == 'good':
                monitoring_dashboard.adherence_score = 8.0
            elif assessment.medication_adherence == 'fair':
                monitoring_dashboard.adherence_score = 5.0
            else:
                monitoring_dashboard.adherence_score = 2.0
            
            # Update side effects score
            if assessment.side_effects_experienced:
                monitoring_dashboard.side_effects_score = 7.0
            else:
                monitoring_dashboard.side_effects_score = 1.0
            
            monitoring_dashboard.last_assessment_date = assessment.assessment_date.date()
            monitoring_dashboard.next_assessment_due = assessment.next_assessment_due
            monitoring_dashboard.save()
            
            # Check for alerts
            create_effectiveness_alerts(patient, prescription, assessment)
            
            messages.success(request, 'Patient assessment completed successfully!')
            return redirect('patient_dashboard', patient_id=patient.id)
    else:
        form = PatientAssessmentForm(doctor_name=doctor_name)
    
    context = {
        'patient': patient,
        'prescription': prescription,
        'form': form,
    }
    
    return render(request, 'amr_core/patient_assessment.html', context)


def create_effectiveness_alerts(patient, prescription, assessment):
    """Create alerts based on assessment results"""
    alerts_created = []
    
    # Check for ineffective medicine
    if assessment.symptom_improvement in ['no_change', 'worsening']:
        alert = MedicineEffectivenessAlert.objects.create(
            patient=patient,
            prescription=prescription,
            alert_type='ineffective',
            priority='high',
            title=f'Medicine appears ineffective for {patient.name}',
            description=f'Patient reports {assessment.symptom_improvement} after treatment with {prescription.antibiotic.name}',
            triggered_by='Patient assessment - symptom improvement',
        )
        alerts_created.append(alert)
    
    # Check for severe side effects
    if assessment.side_effects_experienced and assessment.side_effects_details:
        if any(word in assessment.side_effects_details.lower() for word in ['severe', 'serious', 'severe', 'allergic', 'rash', 'breathing']):
            alert = MedicineEffectivenessAlert.objects.create(
                patient=patient,
                prescription=prescription,
                alert_type='side_effects',
                priority='critical',
                title=f'Severe side effects reported by {patient.name}',
                description=f'Side effects: {assessment.side_effects_details}',
                triggered_by='Patient assessment - side effects',
            )
            alerts_created.append(alert)
    
    # Check for poor adherence
    if assessment.medication_adherence in ['fair', 'poor']:
        alert = MedicineEffectivenessAlert.objects.create(
            patient=patient,
            prescription=prescription,
            alert_type='adherence',
            priority='medium',
            title=f'Poor medication adherence for {patient.name}',
            description=f'Adherence level: {assessment.medication_adherence}',
            triggered_by='Patient assessment - medication adherence',
        )
        alerts_created.append(alert)
    
    # Check for resistance (if patient reports no improvement)
    if assessment.symptom_improvement in ['no_change', 'worsening'] and assessment.medication_adherence == 'excellent':
        alert = MedicineEffectivenessAlert.objects.create(
            patient=patient,
            prescription=prescription,
            alert_type='resistance',
            priority='high',
            title=f'Possible antibiotic resistance for {patient.name}',
            description=f'Patient reports {assessment.symptom_improvement} despite good adherence to {prescription.antibiotic.name}',
            triggered_by='Patient assessment - no improvement with good adherence',
        )
        alerts_created.append(alert)
    
    return alerts_created


@login_required
def medicine_alerts(request):
    """Medicine effectiveness alerts dashboard"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        doctor_name = doctor.name
    except Doctor.DoesNotExist:
        doctor_name = request.user.username
    
    # Get alerts for doctor's patients
    alerts = MedicineEffectivenessAlert.objects.filter(
        prescription__doctor_name__icontains=doctor_name
    ).order_by('-created_date')
    
    # Filter by priority if requested
    priority_filter = request.GET.get('priority')
    if priority_filter:
        alerts = alerts.filter(priority=priority_filter)
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        alerts = alerts.filter(status=status_filter)
    
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'amr_core/medicine_alerts.html', context)


@login_required
def alert_detail(request, alert_id):
    """Alert detail and management"""
    alert = get_object_or_404(MedicineEffectivenessAlert, id=alert_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'acknowledge':
            alert.status = 'acknowledged'
            alert.acknowledged_by = request.user.username
            alert.acknowledged_date = timezone.now()
            alert.save()
            messages.success(request, 'Alert acknowledged successfully!')
        
        elif action == 'resolve':
            alert.status = 'resolved'
            alert.resolution_notes = request.POST.get('resolution_notes', '')
            alert.save()
            messages.success(request, 'Alert resolved successfully!')
        
        elif action == 'update':
            form = MedicineEffectivenessAlertForm(request.POST, instance=alert)
            if form.is_valid():
                form.save()
                messages.success(request, 'Alert updated successfully!')
        
        return redirect('alert_detail', alert_id=alert.id)
    
    form = MedicineEffectivenessAlertForm(instance=alert)
    
    context = {
        'alert': alert,
        'form': form,
    }
    
    return render(request, 'amr_core/alert_detail.html', context)


@login_required
def monitoring_analytics(request):
    """Advanced monitoring analytics dashboard"""
    try:
        doctor = Doctor.objects.get(user=request.user)
        doctor_name = doctor.name
    except Doctor.DoesNotExist:
        doctor_name = request.user.username
    
    # Get doctor's patients
    doctor_patients = Patient.objects.filter(
        prescription__doctor_name__icontains=doctor_name
    ).distinct()
    
    # Get monitoring dashboards
    monitoring_dashboards = PatientMonitoringDashboard.objects.filter(
        patient__in=doctor_patients
    ).order_by('-updated_at')
    
    # Analytics data
    from django.db.models import Avg
    analytics_data = {
        'total_patients_monitored': monitoring_dashboards.count(),
        'patients_at_risk': monitoring_dashboards.filter(treatment_status__in=['concern', 'critical']).count(),
        'patients_on_track': monitoring_dashboards.filter(treatment_status='on_track').count(),
        'average_effectiveness': monitoring_dashboards.aggregate(avg=Avg('effectiveness_score'))['avg'] or 0,
        'average_adherence': monitoring_dashboards.aggregate(avg=Avg('adherence_score'))['avg'] or 0,
        'average_side_effects': monitoring_dashboards.aggregate(avg=Avg('side_effects_score'))['avg'] or 0,
    }
    
    # Recent assessments
    recent_assessments = PatientAssessment.objects.filter(
        patient__in=doctor_patients
    ).order_by('-assessment_date')[:10]
    
    # Treatment effectiveness by antibiotic
    antibiotic_effectiveness = {}
    for dashboard in monitoring_dashboards:
        antibiotic_name = dashboard.prescription.antibiotic.name
        if antibiotic_name not in antibiotic_effectiveness:
            antibiotic_effectiveness[antibiotic_name] = {
                'total': 0,
                'effective': 0,
                'side_effects': 0,
            }
        
        antibiotic_effectiveness[antibiotic_name]['total'] += 1
        if dashboard.effectiveness_score >= 7:
            antibiotic_effectiveness[antibiotic_name]['effective'] += 1
        if dashboard.side_effects_score >= 5:
            antibiotic_effectiveness[antibiotic_name]['side_effects'] += 1
    
    context = {
        'monitoring_dashboards': monitoring_dashboards,
        'analytics_data': analytics_data,
        'recent_assessments': recent_assessments,
        'antibiotic_effectiveness': antibiotic_effectiveness,
    }
    
    return render(request, 'amr_core/monitoring_analytics.html', context)