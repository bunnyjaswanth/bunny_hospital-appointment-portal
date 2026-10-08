from django.contrib import admin
from .models import Doctor, Patient, Appointment, MedicalReport


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'specialization', 'consultation_fee', 'active_status', 'available_days', 'room_number')
    list_filter = ('department', 'active_status')
    search_fields = ('name', 'specialization', 'department')
    list_editable = ('active_status', 'consultation_fee')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'gender', 'blood_group', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('gender', 'blood_group')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'date', 'time_slot', 'status', 'created_date')
    list_filter = ('status', 'doctor__department', 'date', 'doctor')
    search_fields = ('patient__name', 'patient__phone', 'patient__email', 'doctor__name', 'reason')
    list_editable = ('status',)
    date_hierarchy = 'date'


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'created_date')
    search_fields = ('patient__name', 'doctor__name', 'diagnosis', 'prescription')
    list_filter = ('created_date', 'doctor__department')
