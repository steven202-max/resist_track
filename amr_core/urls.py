from django.urls import path
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('doctor/login/', views.doctor_login, name='doctor_login'),
    path('doctor/register/', views.doctor_register, name='doctor_register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Doctor dashboard and patient management
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patients/add/', views.add_patient, name='add_patient'),
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    
    # Prescription management
    path('prescribe/', views.prescribe_antibiotic, name='prescribe_antibiotic'),
    path('prescriptions/<int:prescription_id>/success/', views.prescription_success, name='prescription_success'),
    path('prescriptions/<int:prescription_id>/alternatives/', views.prescription_alternatives, name='prescription_alternatives'),
    
    # Patient feedback (no login required)
    path('feedback/', views.patient_feedback, name='patient_feedback'),
    path('feedback/form/', views.feedback_form, name='feedback_form'),
    
    # Resistance records
    path('resistance/add/', views.add_resistance_record, name='add_resistance_record'),
    path('resistance/', views.resistance_records, name='resistance_records'),
    
    # Reports and analytics
    path('reports/', views.reports, name='reports'),
    
    # Patient monitoring and assessment
    path('patients/<int:patient_id>/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patients/<int:patient_id>/assessment/', views.patient_assessment, name='patient_assessment'),
    path('patients/<int:patient_id>/assessment/<int:prescription_id>/', views.patient_assessment, name='patient_assessment_with_prescription'),
    
    # Medicine effectiveness alerts
    path('alerts/', views.medicine_alerts, name='medicine_alerts'),
    path('alerts/<int:alert_id>/', views.alert_detail, name='alert_detail'),
    
    # Monitoring analytics
    path('monitoring/analytics/', views.monitoring_analytics, name='monitoring_analytics'),
    
    # AJAX endpoints
    path('ajax/check-resistance/', views.check_resistance_ajax, name='check_resistance_ajax'),
    path('ajax/get-alternatives/', views.get_alternatives_ajax, name='get_alternatives_ajax'),
]
