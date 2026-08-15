# Student Leave Management System

A web-based **Student Leave Management System** built with Django. The system allows students to apply for leave, track leave requests, receive notifications, and manage their profiles, while administrators can review, approve, reject, and manage student leave applications.

## 🚀 Features

### 👨‍🎓 Student

* Student registration and login
* Student dashboard
* Profile management
* Apply for leave
* Multiple leave types:

  * Medical Leave
  * Personal Leave
  * Casual Leave
  * Academic Leave
* View leave application history
* Track leave status
* View admin remarks
* Leave balance/limit management
* Upload medical certificates when required
* Leave notifications
* AI-powered leave report generation

### 👨‍💼 Admin

* Admin login
* Admin dashboard
* View registered students
* Manage student accounts
* View all leave applications
* Approve leave applications
* Reject leave applications
* Add remarks to leave applications
* Manage leave records

### 🤖 AI Features

* AI-assisted leave report generation
* Leave reason analysis
* AI integration using Groq API

## 🛠️ Technologies Used

### Backend

* Python
* Django
* SQLite
* Django Templates
* REST/API integration

### Frontend

* HTML
* CSS
* JavaScript
* Bootstrap

### AI

* Groq API

### Other

* ReportLab for PDF generation
* Python-dotenv for environment variables

## 📂 Project Structure

```text
studentleave/
│
├── studentleave/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── studentleaveapp/
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── media/
├── .env
├── .gitignore
├── manage.py
├── requirements.txt
└── db.sqlite3
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd studentleave
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the same directory as `manage.py`.

```env
SECRET_KEY=your-django-secret-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
GROQ_API_KEY=your-groq-api-key
GROQ_API_KEY2=your-groq-api-key
```

> Never upload the `.env` file to GitHub.

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Create an admin account

```bash
python manage.py createsuperuser
```

### 8. Run the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## 🔐 Environment Variables

Sensitive credentials are stored in `.env` instead of directly inside `settings.py`.

The following values should be configured:

| Variable              | Purpose                      |
| --------------------- | ---------------------------- |
| `SECRET_KEY`          | Django security key          |
| `EMAIL_HOST_USER`     | Gmail account used for email |
| `EMAIL_HOST_PASSWORD` | Gmail app password           |
| `GROQ_API_KEY`        | Groq AI API key              |
| `GROQ_API_KEY2`       | Secondary Groq API key       |

The `.env` file is excluded from Git using `.gitignore`.

## 📄 PDF Reports

The project uses **ReportLab** to generate leave-related PDF reports.

## 🔒 Security

The project follows basic security practices for storing sensitive configuration:

* API keys are stored in environment variables.
* Email credentials are stored in environment variables.
* Django secret key is stored in an environment variable.
* `.env` is excluded from Git.
* `.venv` is excluded from Git.
* Database files are excluded from Git.
* Uploaded media files are excluded from Git.

## 🎯 Purpose

This project was developed as a practical Django project to learn and demonstrate:

* Django web development
* Authentication and authorization
* CRUD operations
* Database management
* File uploads
* Email integration
* PDF generation
* API integration
* AI integration
* Git and GitHub project management

## 📌 Future Improvements

Possible future improvements include:

* Advanced role-based permissions
* Email notifications for leave status changes
* Improved analytics dashboard
* Advanced leave statistics
* Better AI-powered leave analysis
* REST API using Django REST Framework
* Automated testing
* Deployment to a cloud platform

## 👨‍💻 Author

**Devanandan V**



## 📜 License

This project is created for educational and portfolio purposes.
