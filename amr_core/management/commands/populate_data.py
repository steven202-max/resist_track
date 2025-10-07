from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from amr_core.models import (
    Patient, Antibiotic, ResistanceRecord, Prescription, 
    Feedback, Doctor, AntibioticEffectiveness, PatientAssessment,
    MedicineEffectivenessAlert, PatientMonitoringDashboard
)
from datetime import date, datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Populate the database with sample data for AMR tracking system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create demo doctor user
        demo_user, created = User.objects.get_or_create(
            username='demo_doctor',
            defaults={
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'demo@example.com',
                'is_staff': True,
            }
        )
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            self.stdout.write('Created demo doctor user')

        # Create demo doctor profile
        demo_doctor, created = Doctor.objects.get_or_create(
            user=demo_user,
            defaults={
                'name': 'Dr. John Smith',
                'license_number': 'MD123456',
                'specialization': 'Infectious Diseases',
                'hospital': 'General Hospital',
                'phone': '+1-555-0123',
                'email': 'demo@example.com',
            }
        )
        if created:
            self.stdout.write('Created demo doctor profile')

        # Create antibiotics
        antibiotics_data = [
            {
                'name': 'Amoxicillin',
                'bacteria_targeted': 'E. coli, Streptococcus pneumoniae, Haemophilus influenzae',
                'class_type': 'penicillin',
                'description': 'Broad-spectrum penicillin antibiotic',
                'dosage_info': '250-500mg every 8 hours',
            },
            {
                'name': 'Ciprofloxacin',
                'bacteria_targeted': 'E. coli, Pseudomonas aeruginosa, Enterococcus',
                'class_type': 'fluoroquinolone',
                'description': 'Fluoroquinolone antibiotic with broad spectrum activity',
                'dosage_info': '250-750mg every 12 hours',
            },
            {
                'name': 'Azithromycin',
                'bacteria_targeted': 'Streptococcus pneumoniae, Haemophilus influenzae, Mycoplasma',
                'class_type': 'macrolide',
                'description': 'Macrolide antibiotic with long half-life',
                'dosage_info': '500mg once daily for 3-5 days',
            },
            {
                'name': 'Ceftriaxone',
                'bacteria_targeted': 'E. coli, Klebsiella, Streptococcus pneumoniae',
                'class_type': 'cephalosporin',
                'description': 'Third-generation cephalosporin',
                'dosage_info': '1-2g once daily IV/IM',
            },
            {
                'name': 'Vancomycin',
                'bacteria_targeted': 'MRSA, Enterococcus, Clostridium difficile',
                'class_type': 'other',
                'description': 'Glycopeptide antibiotic for resistant organisms',
                'dosage_info': '15-20mg/kg every 8-12 hours IV',
            },
            {
                'name': 'Doxycycline',
                'bacteria_targeted': 'Chlamydia, Mycoplasma, Rickettsia',
                'class_type': 'tetracycline',
                'description': 'Tetracycline antibiotic with broad spectrum',
                'dosage_info': '100mg twice daily',
            },
            {
                'name': 'Gentamicin',
                'bacteria_targeted': 'E. coli, Klebsiella, Pseudomonas aeruginosa',
                'class_type': 'aminoglycoside',
                'description': 'Aminoglycoside antibiotic',
                'dosage_info': '3-5mg/kg/day IV/IM',
            },
            {
                'name': 'Trimethoprim/Sulfamethoxazole',
                'bacteria_targeted': 'E. coli, Staphylococcus aureus, Pneumocystis',
                'class_type': 'sulfonamide',
                'description': 'Combination antibiotic with synergistic activity',
                'dosage_info': '160/800mg twice daily',
            },
        ]

        antibiotics = []
        for ab_data in antibiotics_data:
            antibiotic, created = Antibiotic.objects.get_or_create(
                name=ab_data['name'],
                defaults=ab_data
            )
            if created:
                antibiotics.append(antibiotic)
                self.stdout.write(f'Created antibiotic: {antibiotic.name}')

        # Create patients
        patients_data = [
            {
                'name': 'Alice Johnson',
                'age': 34,
                'gender': 'F',
                'phone': '+1-555-0001',
                'email': 'alice.johnson@email.com',
                'medical_history': 'History of recurrent UTIs, diabetes type 2',
                'allergies': 'Penicillin allergy',
            },
            {
                'name': 'Bob Wilson',
                'age': 45,
                'gender': 'M',
                'phone': '+1-555-0002',
                'email': 'bob.wilson@email.com',
                'medical_history': 'Hypertension, previous pneumonia',
                'allergies': 'None known',
            },
            {
                'name': 'Carol Davis',
                'age': 28,
                'gender': 'F',
                'phone': '+1-555-0003',
                'email': 'carol.davis@email.com',
                'medical_history': 'Asthma, seasonal allergies',
                'allergies': 'Sulfa drugs',
            },
            {
                'name': 'David Brown',
                'age': 52,
                'gender': 'M',
                'phone': '+1-555-0004',
                'email': 'david.brown@email.com',
                'medical_history': 'COPD, previous MRSA infection',
                'allergies': 'None known',
            },
            {
                'name': 'Eva Martinez',
                'age': 31,
                'gender': 'F',
                'phone': '+1-555-0005',
                'email': 'eva.martinez@email.com',
                'medical_history': 'Pregnancy, previous UTI',
                'allergies': 'None known',
            },
            {
                'name': 'Frank Taylor',
                'age': 67,
                'gender': 'M',
                'phone': '+1-555-0006',
                'email': 'frank.taylor@email.com',
                'medical_history': 'Diabetes, heart disease, previous pneumonia',
                'allergies': 'Penicillin allergy',
            },
        ]

        patients = []
        for patient_data in patients_data:
            patient, created = Patient.objects.get_or_create(
                name=patient_data['name'],
                defaults=patient_data
            )
            if created:
                patients.append(patient)
                self.stdout.write(f'Created patient: {patient.name}')

        # Create resistance records
        resistance_data = [
            {'patient': 'Alice Johnson', 'antibiotic': 'Amoxicillin', 'result': 'resistant', 'test_date': date(2024, 1, 15)},
            {'patient': 'Bob Wilson', 'antibiotic': 'Ciprofloxacin', 'result': 'sensitive', 'test_date': date(2024, 2, 10)},
            {'patient': 'Carol Davis', 'antibiotic': 'Trimethoprim/Sulfamethoxazole', 'result': 'resistant', 'test_date': date(2024, 1, 20)},
            {'patient': 'David Brown', 'antibiotic': 'Vancomycin', 'result': 'sensitive', 'test_date': date(2024, 3, 5)},
            {'patient': 'Frank Taylor', 'antibiotic': 'Amoxicillin', 'result': 'resistant', 'test_date': date(2024, 2, 28)},
            {'patient': 'Alice Johnson', 'antibiotic': 'Ciprofloxacin', 'result': 'sensitive', 'test_date': date(2024, 2, 15)},
            {'patient': 'Bob Wilson', 'antibiotic': 'Azithromycin', 'result': 'intermediate', 'test_date': date(2024, 2, 20)},
        ]

        for res_data in resistance_data:
            patient = Patient.objects.get(name=res_data['patient'])
            antibiotic = Antibiotic.objects.get(name=res_data['antibiotic'])
            resistance_record, created = ResistanceRecord.objects.get_or_create(
                patient=patient,
                antibiotic=antibiotic,
                defaults={
                    'result': res_data['result'],
                    'test_date': res_data['test_date'],
                    'test_method': 'MIC (Minimum Inhibitory Concentration)',
                    'notes': f'Test performed at {random.choice(["Lab A", "Lab B", "Hospital Lab"])}',
                }
            )
            if created:
                self.stdout.write(f'Created resistance record: {patient.name} - {antibiotic.name}')

        # Create prescriptions
        prescriptions_data = [
            {
                'patient': 'Alice Johnson',
                'antibiotic': 'Amoxicillin',
                'diagnosis': 'Urinary tract infection',
                'dosage': '500mg',
                'frequency': 'Three times daily',
                'duration': '7 days',
                'date_prescribed': datetime.now() - timedelta(days=10),
                'status': 'completed',
            },
            {
                'patient': 'Bob Wilson',
                'antibiotic': 'Ceftriaxone',
                'diagnosis': 'Community-acquired pneumonia',
                'dosage': '1g',
                'frequency': 'Once daily',
                'duration': '7 days',
                'date_prescribed': datetime.now() - timedelta(days=8),
                'status': 'completed',
            },
            {
                'patient': 'Carol Davis',
                'antibiotic': 'Azithromycin',
                'diagnosis': 'Upper respiratory tract infection',
                'dosage': '500mg',
                'frequency': 'Once daily',
                'duration': '5 days',
                'date_prescribed': datetime.now() - timedelta(days=5),
                'status': 'active',
            },
            {
                'patient': 'David Brown',
                'antibiotic': 'Vancomycin',
                'diagnosis': 'MRSA skin infection',
                'dosage': '15mg/kg',
                'frequency': 'Every 12 hours',
                'duration': '10 days',
                'date_prescribed': datetime.now() - timedelta(days=3),
                'status': 'active',
            },
            {
                'patient': 'Eva Martinez',
                'antibiotic': 'Ciprofloxacin',
                'diagnosis': 'Urinary tract infection',
                'dosage': '250mg',
                'frequency': 'Twice daily',
                'duration': '7 days',
                'date_prescribed': datetime.now() - timedelta(days=7),
                'status': 'completed',
            },
            {
                'patient': 'Frank Taylor',
                'antibiotic': 'Amoxicillin',
                'diagnosis': 'Community-acquired pneumonia',
                'dosage': '875mg',
                'frequency': 'Twice daily',
                'duration': '10 days',
                'date_prescribed': datetime.now() - timedelta(days=2),
                'status': 'active',
            },
        ]

        prescriptions = []
        for pres_data in prescriptions_data:
            patient = Patient.objects.get(name=pres_data['patient'])
            antibiotic = Antibiotic.objects.get(name=pres_data['antibiotic'])
            prescription, created = Prescription.objects.get_or_create(
                patient=patient,
                antibiotic=antibiotic,
                diagnosis=pres_data['diagnosis'],
                defaults={
                    'doctor_name': 'Dr. John Smith',
                    'dosage': pres_data['dosage'],
                    'frequency': pres_data['frequency'],
                    'duration': pres_data['duration'],
                    'date_prescribed': pres_data['date_prescribed'],
                    'status': pres_data['status'],
                    'notes': f'Prescribed for {pres_data["diagnosis"]}',
                }
            )
            prescriptions.append(prescription)
            if created:
                self.stdout.write(f'Created prescription: {patient.name} - {antibiotic.name}')
            else:
                self.stdout.write(f'Found existing prescription: {patient.name} - {antibiotic.name}')

        # Create feedback
        feedback_data = [
            {'patient': 'Alice Johnson', 'antibiotic': 'Amoxicillin', 'feedback': 'no_improvement', 'details': 'Symptoms persisted, no improvement after 5 days'},
            {'patient': 'Bob Wilson', 'antibiotic': 'Ceftriaxone', 'feedback': 'recovered', 'details': 'Complete recovery, symptoms resolved within 5 days'},
            {'patient': 'Eva Martinez', 'antibiotic': 'Ciprofloxacin', 'feedback': 'recovered', 'details': 'Successful treatment, symptoms cleared in 3 days'},
        ]

        for fb_data in feedback_data:
            patient = Patient.objects.get(name=fb_data['patient'])
            antibiotic = Antibiotic.objects.get(name=fb_data['antibiotic'])
            prescription = Prescription.objects.get(patient=patient, antibiotic=antibiotic)
            
            feedback, created = Feedback.objects.get_or_create(
                patient=patient,
                prescription=prescription,
                defaults={
                    'feedback': fb_data['feedback'],
                    'details': fb_data['details'],
                    'severity_rating': random.randint(3, 8),
                }
            )
            if created:
                self.stdout.write(f'Created feedback: {patient.name} - {antibiotic.name}')

        # Create antibiotic effectiveness records
        for antibiotic in antibiotics:
            for bacteria in ['E. coli', 'Streptococcus pneumoniae', 'MRSA']:
                if bacteria.lower() in antibiotic.bacteria_targeted.lower():
                    effectiveness, created = AntibioticEffectiveness.objects.get_or_create(
                        antibiotic=antibiotic,
                        bacteria_type=bacteria,
                        defaults={
                            'total_prescriptions': random.randint(5, 25),
                            'successful_treatments': random.randint(3, 20),
                            'failed_treatments': random.randint(1, 5),
                            'side_effects_reported': random.randint(0, 3),
                        }
                    )
                    if created:
                        self.stdout.write(f'Created effectiveness record: {antibiotic.name} vs {bacteria}')

        # Create sample patient assessments
        if prescriptions:
            self.create_sample_assessments(demo_doctor, patients, prescriptions)
            
            # Create sample monitoring dashboards
            self.create_sample_monitoring_dashboards(patients, prescriptions)
            
            # Create sample alerts
            self.create_sample_alerts(patients, prescriptions)
        else:
            self.stdout.write('No prescriptions found. Skipping monitoring data creation.')

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
        self.stdout.write('Demo login credentials:')
        self.stdout.write('Username: demo_doctor')
        self.stdout.write('Password: demo123')

    def create_sample_assessments(self, doctor, patients, prescriptions):
        """Create sample patient assessments"""
        self.stdout.write('Creating sample patient assessments...')
        
        assessment_types = ['initial', 'follow_up', 'side_effects', 'effectiveness']
        symptom_improvements = ['significant', 'moderate', 'minimal', 'no_change', 'worsening']
        adherence_levels = ['excellent', 'good', 'fair', 'poor']
        satisfaction_levels = ['very_satisfied', 'satisfied', 'neutral', 'dissatisfied', 'very_dissatisfied']
        
        for i, prescription in enumerate(prescriptions[:5]):  # Create assessments for first 5 prescriptions
            patient = prescription.patient
            
            # Create 1-3 assessments per patient
            num_assessments = random.randint(1, 3)
            for j in range(num_assessments):
                assessment_date = prescription.date_prescribed + timedelta(days=random.randint(1, 10))
                
                assessment = PatientAssessment.objects.create(
                    patient=patient,
                    prescription=prescription,
                    assessment_type=random.choice(assessment_types),
                    assessment_date=assessment_date,
                    conducted_by=doctor.name,
                    symptom_improvement=random.choice(symptom_improvements),
                    side_effects_experienced=random.choice([True, False]),
                    side_effects_details="Mild nausea and headache" if random.choice([True, False]) else "",
                    medication_adherence=random.choice(adherence_levels),
                    pain_level=random.randint(1, 10) if random.choice([True, False]) else None,
                    energy_level=random.choice(['excellent', 'good', 'fair', 'poor']),
                    appetite_changes=random.choice(['improved', 'same', 'decreased', 'lost']),
                    sleep_quality=random.choice(['excellent', 'good', 'fair', 'poor']),
                    additional_symptoms="Feeling better overall" if random.choice([True, False]) else "",
                    overall_satisfaction=random.choice(satisfaction_levels),
                    doctor_notes=f"Patient responding well to treatment. Continue monitoring.",
                    next_assessment_due=assessment_date + timedelta(days=random.randint(3, 7))
                )
                
                self.stdout.write(f'Created assessment for {patient.name} on {assessment_date.date()}')

    def create_sample_monitoring_dashboards(self, patients, prescriptions):
        """Create sample monitoring dashboards"""
        self.stdout.write('Creating sample monitoring dashboards...')
        
        for prescription in prescriptions[:8]:  # Create dashboards for first 8 prescriptions
            patient = prescription.patient
            
            # Calculate scores based on random values
            effectiveness_score = random.uniform(6.0, 9.5)
            adherence_score = random.uniform(7.0, 10.0)
            side_effects_score = random.uniform(1.0, 6.0)
            
            # Determine treatment status based on scores
            if effectiveness_score >= 8 and adherence_score >= 8 and side_effects_score <= 3:
                treatment_status = 'on_track'
            elif effectiveness_score >= 6 and adherence_score >= 6 and side_effects_score <= 5:
                treatment_status = 'monitoring'
            elif effectiveness_score < 5 or adherence_score < 5 or side_effects_score > 7:
                treatment_status = 'critical'
            else:
                treatment_status = 'concern'
            
            dashboard = PatientMonitoringDashboard.objects.create(
                patient=patient,
                prescription=prescription,
                treatment_start_date=prescription.date_prescribed.date(),
                expected_completion_date=prescription.date_prescribed.date() + timedelta(days=7),
                last_assessment_date=prescription.date_prescribed.date() + timedelta(days=random.randint(2, 5)),
                next_assessment_due=prescription.date_prescribed.date() + timedelta(days=random.randint(8, 12)),
                treatment_status=treatment_status,
                effectiveness_score=effectiveness_score,
                adherence_score=adherence_score,
                side_effects_score=side_effects_score,
                high_risk_factors="Patient with allergies" if patient.allergies else "",
                monitoring_notes=f"Regular monitoring required for {patient.name}. Treatment progressing as expected."
            )
            
            self.stdout.write(f'Created monitoring dashboard for {patient.name} - Status: {treatment_status}')

    def create_sample_alerts(self, patients, prescriptions):
        """Create sample medicine effectiveness alerts"""
        self.stdout.write('Creating sample medicine effectiveness alerts...')
        
        if not prescriptions:
            self.stdout.write('No prescriptions available for alert creation.')
            return
        
        alert_types = ['ineffective', 'side_effects', 'adherence', 'resistance']
        priorities = ['low', 'medium', 'high', 'critical']
        
        # Create 3-5 sample alerts
        num_alerts = min(random.randint(3, 5), len(prescriptions))
        for i in range(num_alerts):
            prescription = random.choice(prescriptions)
            patient = prescription.patient
            
            alert_type = random.choice(alert_types)
            priority = random.choice(priorities)
            
            if alert_type == 'ineffective':
                title = f"Medicine appears ineffective for {patient.name}"
                description = f"Patient reports no improvement after 5 days of treatment with {prescription.antibiotic.name}"
                triggered_by = "Patient assessment - no symptom improvement"
            elif alert_type == 'side_effects':
                title = f"Side effects reported by {patient.name}"
                description = f"Patient experiencing nausea, vomiting, and rash with {prescription.antibiotic.name}"
                triggered_by = "Patient feedback - severe side effects"
            elif alert_type == 'adherence':
                title = f"Poor medication adherence for {patient.name}"
                description = f"Patient missing doses of {prescription.antibiotic.name}. Adherence rate below 70%"
                triggered_by = "Patient assessment - poor adherence"
            else:  # resistance
                title = f"Possible antibiotic resistance for {patient.name}"
                description = f"Patient shows no improvement despite good adherence to {prescription.antibiotic.name}"
                triggered_by = "Clinical assessment - no response to treatment"
            
            alert = MedicineEffectivenessAlert.objects.create(
                patient=patient,
                prescription=prescription,
                alert_type=alert_type,
                priority=priority,
                title=title,
                description=description,
                triggered_by=triggered_by,
                status='active'
            )
            
            self.stdout.write(f'Created {priority} alert: {title}')
