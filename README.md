# AMR Tracking System

A comprehensive Django-based web application for tracking Antimicrobial Resistance (AMR), managing antibiotic prescriptions, and monitoring patient feedback to improve clinical decision-making.

## 🎯 System Overview

The AMR Tracking System is designed to help healthcare professionals make evidence-based antibiotic prescribing decisions by:

- **Real-time Resistance Checking**: Automatically checks patient resistance history before prescribing
- **Alternative Suggestions**: Provides intelligent recommendations for alternative antibiotics
- **Effectiveness Tracking**: Monitors antibiotic performance through patient feedback
- **Comprehensive Analytics**: Generates detailed reports and visualizations

## 🚀 Key Features

### For Doctors
- **Dashboard**: Overview of prescriptions, resistance alerts, and key metrics
- **Patient Management**: Add, view, and manage patient information
- **Smart Prescribing**: Real-time resistance checking with alternative suggestions
- **Resistance Records**: Track and manage patient resistance history
- **Analytics**: Comprehensive reports with Chart.js visualizations

### For Patients
- **Feedback System**: Easy-to-use feedback forms for treatment outcomes
- **No Login Required**: Simple ID-based access for patient feedback

### System Features
- **Resistance Detection**: Automatic alerts for known resistance patterns
- **Alternative Recommendations**: Smart suggestions based on bacteria targeting
- **Effectiveness Analytics**: Track antibiotic success rates and performance
- **Modern UI**: Bootstrap 5 with responsive design
- **Admin Interface**: Comprehensive Django admin for data management

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (easily configurable for PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5, Chart.js
- **Icons**: Bootstrap Icons
- **Authentication**: Django's built-in user authentication

## 📋 System Requirements

- Python 3.8+
- Django 4.2+
- Modern web browser with JavaScript enabled

## 🚀 Installation & Setup

### 1. Clone/Download the Project
```bash
cd C:\xampp\htdocs\Resist_Track
```

### 2. Install Dependencies
```bash
pip install django
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Sample Data
```bash
python manage.py populate_data
```

### 5. Start Development Server
```bash
python manage.py runserver
```

### 6. Access the Application
Open your browser and navigate to: `http://127.0.0.1:8000`

## 👤 Demo Access

**Demo Doctor Account:**
- Username: `demo_doctor`
- Password: `demo123`

## 📊 Database Models

### Core Models
- **Patient**: Patient information and medical history
- **Antibiotic**: Antibiotic details with bacteria targeting
- **ResistanceRecord**: Patient resistance history
- **Prescription**: Prescription details with status tracking
- **Feedback**: Patient treatment feedback
- **Doctor**: Doctor profiles and credentials
- **AntibioticEffectiveness**: Effectiveness statistics

### Key Relationships
- Patient → ResistanceRecord (One-to-Many)
- Patient → Prescription (One-to-Many)
- Antibiotic → Prescription (One-to-Many)
- Prescription → Feedback (One-to-One)

## 🔄 System Workflow

### 1. Doctor Workflow
1. **Login** → Access doctor dashboard
2. **Add Patient** → Register patient information
3. **Prescribe** → Select antibiotic with resistance checking
4. **Monitor** → View resistance alerts and alternatives
5. **Analyze** → Review effectiveness reports

### 2. Patient Workflow
1. **Receive Prescription** → Get Patient ID and Prescription ID
2. **Provide Feedback** → Use IDs to access feedback form
3. **Report Outcome** → Select recovery status and details

### 3. System Logic
1. **Resistance Check** → Real-time checking against patient history
2. **Alternative Suggestions** → Smart recommendations for resistant cases
3. **Effectiveness Tracking** → Monitor success rates and patterns
4. **Analytics Generation** → Create comprehensive reports

## 📱 User Interface

### Home Page
- System overview with key statistics
- Quick access to main features
- Demo workflow explanation

### Doctor Dashboard
- Recent prescriptions overview
- Resistance alerts
- Quick action buttons
- Key performance metrics

### Prescription Form
- Real-time resistance checking
- Alternative antibiotic suggestions
- Comprehensive prescription details
- AJAX-powered interactions

### Patient Feedback
- Simple ID-based access
- Multiple feedback options
- Detailed reporting capabilities
- No login required

### Reports & Analytics
- Interactive Chart.js visualizations
- Antibiotic effectiveness rates
- Resistance distribution analysis
- Recent feedback summaries

## 🔧 Configuration

### Settings
- Database configuration in `amr_demo/settings.py`
- Static files configuration
- App registration

### Admin Interface
Access at: `http://127.0.0.1:8000/admin/`

Create superuser:
```bash
python manage.py createsuperuser
```

## 📈 Key Metrics Tracked

- **Antibiotic Effectiveness Rates**: Success percentages per antibiotic
- **Resistance Patterns**: Distribution of resistance types
- **Patient Outcomes**: Recovery, side effects, and complications
- **Prescription Volume**: Usage statistics and trends
- **Alternative Usage**: Frequency of alternative prescriptions

## 🛡️ Security Features

- **User Authentication**: Secure login system for doctors
- **CSRF Protection**: Built-in Django CSRF protection
- **Data Validation**: Comprehensive form validation
- **Admin Security**: Protected admin interface

## 🔮 Future Enhancements

### Planned Features
- **Lab Integration**: Connect with laboratory systems
- **API Development**: RESTful API for external integrations
- **Mobile App**: Native mobile application
- **Advanced Analytics**: Machine learning predictions
- **Multi-language Support**: Internationalization
- **Backup & Recovery**: Automated data backup

### Scalability Options
- **Database Migration**: PostgreSQL/MySQL support
- **Cloud Deployment**: AWS/Azure compatibility
- **Load Balancing**: Multi-server deployment
- **Caching**: Redis/Memcached integration

## 📚 API Endpoints

### AJAX Endpoints
- `/ajax/check-resistance/` - Real-time resistance checking
- `/ajax/get-alternatives/` - Alternative antibiotic suggestions

### Main URLs
- `/` - Home page
- `/doctor/login/` - Doctor authentication
- `/doctor/dashboard/` - Doctor dashboard
- `/prescribe/` - Prescription form
- `/feedback/` - Patient feedback
- `/reports/` - Analytics and reports

## 🐛 Troubleshooting

### Common Issues
1. **Static Files Not Loading**: Check STATICFILES_DIRS in settings
2. **Database Errors**: Run migrations with `python manage.py migrate`
3. **Permission Errors**: Ensure proper file permissions
4. **Port Already in Use**: Change port with `python manage.py runserver 8001`

### Debug Mode
Set `DEBUG = True` in `settings.py` for detailed error messages.

## 📞 Support

For technical support or questions:
- Check Django documentation: https://docs.djangoproject.com/
- Review the code comments and docstrings
- Use Django debug toolbar for development

## 📄 License

This project is developed as a demonstration system for AMR tracking. Please ensure compliance with healthcare data regulations in your jurisdiction.

---

**Built with ❤️ using Django and Bootstrap**

*Last updated: December 2024*
