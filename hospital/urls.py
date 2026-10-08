from django.urls import path
from . import views

urlpatterns = [
    # Public & Patient Navigation
    path('', views.home, name='home'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),

    # Interactive Slot API
    path('api/slots/', views.check_slots_api, name='check_slots_api'),

    # Admin & Staff Workflows
    path('staff/appointments/', views.staff_appointments, name='staff_appointments'),
    path('staff/appointments/<int:pk>/status/', views.update_appointment_status, name='update_appointment_status'),
    path('staff/appointments/<int:pk>/report/', views.manage_medical_report, name='manage_medical_report'),
    path('staff/doctors/', views.staff_doctors, name='staff_doctors'),
    path('staff/doctors/<int:pk>/toggle/', views.toggle_doctor_status, name='toggle_doctor_status'),

    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
]
