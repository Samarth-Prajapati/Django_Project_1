# Django Team Production Report

A comprehensive Django-based web application for tracking team productivity, managing project resources, and generating detailed production reports with visualization capabilities.

## 📋 Features

- **Resource Management**: Track team members' working days, present hours, and productivity metrics
- **Project Tracking**: Manage projects with different types (Regular, Fixed Cost, Hourly)
- **Time Tracking**: Monitor billable vs non-billable hours for accurate reporting
- **Data Visualization**: Generate charts and graphs for productivity analysis
- **Interactive Project Tree**: Modern Canvas-based interactive project hierarchy visualization with drag, zoom, and search capabilities
- **Excel Import**: Bulk import team production data from Excel files
- **Monthly/Yearly Reports**: Filter and view reports by specific time periods
- **Dashboard Analytics**: Comprehensive dashboard with productivity insights

## 🛠️ Technology Stack

- **Backend**: Django 5.2.4
- **Database**: SQLite3 (default, easily configurable for PostgreSQL/MySQL)
- **Visualization**: Matplotlib, HTML5 Canvas
- **Data Processing**: Pandas (for Excel imports)
- **Frontend**: HTML5, CSS3, JavaScript with Bootstrap 5

## 📁 Project Structure

```
Django-ProductReport/
├── Team_Production_Report/     # Main Django project settings
├── projects/                   # Project management app
│   ├── models.py              # Project model definitions
│   ├── views.py               # Project views and dashboard
│   ├── forms.py               # Project forms
│   ├── templates/             # Project templates
│   └── management/commands/   # Custom Django commands
├── resources/                 # Resource (team member) management app
│   ├── models.py              # Resource model definitions
│   ├── views.py               # Resource views
│   ├── forms.py               # Resource forms
│   ├── templates/             # Resource templates
│   └── management/commands/   # Excel import commands
├── static/                    # Static files (CSS, JS, images)
├── templates/                 # Global templates
├── requirements.txt           # Python dependencies
└── manage.py                  # Django management script
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Graphviz (for tree visualization)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Django-ProductReport-source_django
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Graphviz

#### Windows:

```bash
# Using winget (Windows 10/11)
winget install graphviz

# Or download from: https://graphviz.org/download/
```

#### Linux (Ubuntu/Debian):

```bash
sudo apt-get install graphviz
```

#### macOS:

```bash
brew install graphviz
```

**Note**: After installing Graphviz, ensure it's added to your system PATH. See `GRAPHVIZ_SETUP.md` for detailed instructions.

### 5. Database Setup

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 📊 Usage

### Dashboard

Access the main dashboard at the root URL to view:

- Team productivity overview
- Project statistics
- Monthly/yearly filtering options
- Visual charts and graphs

### Managing Resources

1. Navigate to `/resources/` to add team members
2. Enter resource details including:
   - Resource name
   - Year and month
   - Working days (auto-calculated if not provided)
   - Present days and hours

### Managing Projects

1. Go to `/projects/` to create and manage projects
2. Configure project details:
   - Project name and type
   - Assigned resources
   - Billable/non-billable hours
   - Time tracking information

### Excel Import

Import team production data from Excel files:

```bash
# Import resources
python manage.py import_resource_excel path/to/your/excel_file.xlsx

# Import team production data
python manage.py import_team_production path/to/your/excel_file.xlsx
```

**Excel Format Requirements**:

- Columns should include: `resource_name`, `project_name`, `year`, `month`, `billable_days`, `non_billable_days`
- Ensure proper date formatting and numeric values

## 🔧 Configuration

### Database Configuration

To use PostgreSQL or MySQL instead of SQLite, update `Team_Production_Report/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Environment Variables

For production deployment, consider setting:

- `DEBUG = False`
- `SECRET_KEY` as environment variable
- Database credentials
- `ALLOWED_HOSTS` configuration

## 📈 Key Models

### Resource Model

Represents team members with tracking capabilities:

- Resource name, year, month
- Working days calculation
- Present days and hours tracking
- Productivity counting

### Project Model

Manages project information:

- Project name and type classification
- Resource assignments (many-to-many relationship)
- Time tracking (billable/non-billable days)
- Monthly/yearly organization

## 🎯 Features in Detail

### Automatic Calculations

- **Working Days**: Auto-calculated as Mon-Fri + first Saturday if not manually set
- **Present Hours**: Automatically computed as present_day × 8 hours
- **Productivity Metrics**: Real-time calculation of team productivity ratios

### Visualization

- **Project Trees**: Hierarchical project visualization using Graphviz
- **Productivity Charts**: Matplotlib-generated charts for data analysis
- **Dashboard Widgets**: Interactive elements for quick insights

### Data Import/Export

- **Excel Integration**: Seamless import of production data
- **Bulk Operations**: Efficient handling of large datasets
- **Data Validation**: Built-in validation for imported data

## 🚀 Deployment

### For Production

1. Set environment variables:

```bash
export DJANGO_SETTINGS_MODULE=Team_Production_Report.settings
export DEBUG=False
export SECRET_KEY=your-secret-key
```

2. Collect static files:

```bash
python manage.py collectstatic
```

3. Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn Team_Production_Report.wsgi:application
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Graphviz Not Found**: Ensure Graphviz is installed and added to PATH
2. **Database Errors**: Run migrations if models have changed
3. **Import Errors**: Check Excel file format and column names
4. **Static Files**: Run `collectstatic` if CSS/JS not loading

### Getting Help

- Check the Django documentation: https://docs.djangoproject.com/
- Review Graphviz setup instructions in `GRAPHVIZ_SETUP.md`
- Ensure all dependencies are properly installed

## 📧 Support

For support and questions, please open an issue in the repository or contact the development team.

---

**Version**: 1.0.0  
**Django Version**: 5.2.4  
**Python Version**: 3.8+
