from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Department(models.TextChoices):
    CARDIOLOGY = 'Cardiology', 'Cardiology'
    PEDIATRICS = 'Pediatrics', 'Pediatrics'
    ORTHOPEDICS = 'Orthopedics', 'Orthopedics'
    NEUROLOGY = 'Neurology', 'Neurology'
    DERMATOLOGY = 'Dermatology', 'Dermatology'
    GENERAL = 'General Medicine', 'General Medicine'


class Doctor(models.Model):
    name = models.CharField(max_length=150, help_text="Full Name with Title (e.g. Dr. Jane Smith)")
    department = models.CharField(max_length=50, choices=Department.choices, default=Department.CARDIOLOGY)
    specialization = models.CharField(max_length=150, help_text="Specialization or sub-discipline")
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=75.00)
    available_days = models.CharField(max_length=120, default="Monday, Tuesday, Wednesday, Thursday, Friday")
    active_status = models.BooleanField(default=True, help_text="Is doctor actively taking appointments?")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    room_number = models.CharField(max_length=20, default="Room 201")
    experience_years = models.PositiveIntegerField(default=8)
    bio = models.TextField(blank=True, help_text="Short professional summary")
    avatar_color = models.CharField(max_length=30, default="primary", help_text="Bootstrap theme color for avatar")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.department})"

    @property
    def badge_class(self):
        colors = {
            'Cardiology': 'danger',
            'Pediatrics': 'warning',
            'Orthopedics': 'info',
            'Neurology': 'primary',
            'Dermatology': 'success',
            'General Medicine': 'secondary'
        }
        return colors.get(self.department, 'dark')


class Patient(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients')
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Appointment(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_CONFIRMED = 'Confirmed'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    TIME_SLOT_CHOICES = [
        ('09:00 AM - 09:30 AM', '09:00 AM - 09:30 AM'),
        ('09:30 AM - 10:00 AM', '09:30 AM - 10:00 AM'),
        ('10:00 AM - 10:30 AM', '10:00 AM - 10:30 AM'),
        ('10:30 AM - 11:00 AM', '10:30 AM - 11:00 AM'),
        ('11:00 AM - 11:30 AM', '11:00 AM - 11:30 AM'),
        ('11:30 AM - 12:00 PM', '11:30 AM - 12:00 PM'),
        ('02:00 PM - 02:30 PM', '02:00 PM - 02:30 PM'),
        ('02:30 PM - 03:00 PM', '02:30 PM - 03:00 PM'),
        ('03:00 PM - 03:30 PM', '03:00 PM - 03:30 PM'),
        ('03:30 PM - 04:00 PM', '03:30 PM - 04:00 PM'),
        ('04:00 PM - 04:30 PM', '04:00 PM - 04:30 PM'),
        ('04:30 PM - 05:00 PM', '04:30 PM - 05:00 PM'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time_slot = models.CharField(max_length=50, choices=TIME_SLOT_CHOICES)
    reason = models.TextField(help_text="Chief complaint or reason for visit")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_date = models.DateTimeField(auto_now_add=True)
    admin_notes = models.TextField(blank=True, null=True, help_text="Notes from doctor or receptionist")

    class Meta:
        ordering = ['-date', 'time_slot']

    def __str__(self):
        return f"Appt #{self.id}: {self.patient.name} with {self.doctor.name} on {self.date} [{self.status}]"

    def clean(self):
        super().clean()
        # 1. Prevent booking dates in the past (only for new appointments or when date changed)
        if self.date and self.date < timezone.localdate():
            if not self.pk:
                raise ValidationError({'date': "Appointment date cannot be in the past. Please select today or a future date."})

        # 2. Prevent double booking for the same doctor, date and time slot
        if self.doctor_id and self.date and self.time_slot and self.status != self.STATUS_CANCELLED:
            conflict_query = Appointment.objects.filter(
                doctor=self.doctor,
                date=self.date,
                time_slot=self.time_slot
            ).exclude(status=self.STATUS_CANCELLED)

            if self.pk:
                conflict_query = conflict_query.exclude(pk=self.pk)

            if conflict_query.exists():
                raise ValidationError({
                    'time_slot': f"{self.doctor.name} already has a booked appointment on {self.date} during slot {self.time_slot}. Please select another slot or date."
                })

    @property
    def status_badge_class(self):
        mapping = {
            self.STATUS_PENDING: 'warning text-dark',
            self.STATUS_CONFIRMED: 'primary',
            self.STATUS_COMPLETED: 'success',
            self.STATUS_CANCELLED: 'danger',
        }
        return mapping.get(self.status, 'secondary')


class MedicalReport(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_reports')
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medical_report'
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_reports')
    diagnosis = models.TextField(help_text="Clinical findings and diagnosis")
    prescription = models.TextField(help_text="Medications, dosages, and instructions")
    notes = models.TextField(blank=True, null=True, help_text="Additional recovery recommendations and follow-up")
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f"Report #{self.id} for {self.patient.name} by {self.doctor.name} ({self.created_date.strftime('%Y-%m-%d')})"
