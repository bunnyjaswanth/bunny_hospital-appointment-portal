# 🏥 MediCare+ Hospital & Patient Appointment Management Portal

A full-stack Django web application for managing hospital appointments, doctor schedules, and medical consultation reports.

## 🚀 Live Demo

Deployed on Render: [hospital-appointment-portal-demo.onrender.com](https://hospital-appointment-portal-demo.onrender.com)

---

## 📋 Features

- **Doctor Directory** — Browse and filter specialists by department (Cardiology, Pediatrics, Orthopedics, Neurology)
- **Real-Time Slot Booking** — Interactive appointment slot selector that highlights booked vs available times
- **Double-Booking Prevention** — Server-side and client-side validation prevents duplicate bookings
- **Patient Dashboard** — View upcoming and past appointments with status badges
- **Staff/Admin Panel** — Confirm, complete, or cancel appointments; add medical reports
- **Status Badges** — Pending · Confirmed · Completed · Cancelled
- **Django Admin** — Full model management at `/admin/`

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Framework | Django 6.x |
| Database | SQLite (Django default) |
| Frontend | Bootstrap 5, JavaScript ES6+ |
| Server | Gunicorn |
| Static Files | WhiteNoise |
| Deployment | Render |

---

## 📁 Project Structure

```
bunny/
├── manage.py
├── requirements.txt
├── render.yaml
├── create_superuser.py       # Seeds admin + sample data
├── db.sqlite3
├── sbj/                      # Django project package
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── hospital/                 # Main application
    ├── models.py             # Doctor, Patient, Appointment, MedicalReport
    ├── views.py              # All page views + /api/slots/ JSON endpoint
    ├── forms.py              # ModelForms with validation
    ├── urls.py               # URL routing
    ├── admin.py              # Admin configuration
    ├── tests.py              # Unit tests (7 test cases)
    ├── templates/hospital/   # HTML templates
    │   ├── base.html
    │   ├── home.html
    │   ├── doctor_list.html
    │   ├── book_appointment.html
    │   ├── appointment_detail.html
    │   ├── patient_dashboard.html
    │   ├── staff_appointments.html
    │   ├── staff_doctors.html
    │   ├── medical_report_form.html
    │   ├── login.html
    │   └── register.html
    └── static/
        ├── css/style.css
        └── js/main.js
```

---

## ⚙️ Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/bunnyjaswanth/bunny_hospital-appointment-portal.git
cd bunny_hospital-appointment-portal

# 2. Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Create superuser and seed sample data
python create_superuser.py

# 6. Start development server
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

**Default admin credentials:** `admin` / `admin123`

---

## 🧪 Running Tests

```bash
python manage.py test
```

7 test cases covering:
- Home page load
- Doctor department filtering
- Interactive slots API
- Double-booking prevention
- Past-date booking rejection
- Successful booking and redirect
- Staff status update workflow

---

## 🌐 Render Deployment

The `render.yaml` blueprint configures automatic deployment:

- **Build:** installs dependencies, runs `collectstatic`, `migrate`, and seeds data
- **Start:** launches Gunicorn serving `sbj.wsgi:application`
- **Environment:** `RENDER=True` → `DEBUG=False`, auto-generated `SECRET_KEY`

### Deploy Steps

1. Push this repo to GitHub
2. Log in to [Render](https://render.com) → **New + → Blueprint**
3. Connect this repository
4. Render auto-reads `render.yaml` and creates the service
5. Visit `https://<service-name>.onrender.com`

> **Note:** Render free tier uses an ephemeral filesystem — SQLite data resets on each redeploy. This is acceptable for a demo/learning project.

---

## 🔐 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin/Staff | `admin` | `admin123` |

Change the password after first login via `/admin/` → Users.

---

## 📌 Key URLs

| URL | Description |
|-----|-------------|
| `/` | Home / Landing page |
| `/doctors/` | Doctor list & filter |
| `/book/` | Book appointment |
| `/dashboard/` | Patient dashboard |
| `/staff/appointments/` | Staff management panel |
| `/api/slots/` | JSON slot availability API |
| `/admin/` | Django admin |
| `/login/` | Login |
| `/register/` | Register new patient |

---

## 📝 License

This project is a Django Full-Stack Capstone Assignment for academic purposes.
