from django import forms
from django.utils import timezone
from .models import Doctor, Patient, Appointment, MedicalReport


class AppointmentBookingForm(forms.ModelForm):
    # Patient info fields integrated into booking workflow
    patient_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter full patient name',
            'required': 'required'
        })
    )
    patient_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
            'required': 'required'
        })
    )
    patient_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 000-0000',
            'required': 'required'
        })
    )
    patient_gender = forms.ChoiceField(
        choices=Patient.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    patient_blood_group = forms.ChoiceField(
        choices=[('', 'Select Blood Group (Optional)')] + Patient.BLOOD_GROUPS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time_slot', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={
                'class': 'form-select select-doctor',
                'id': 'id_doctor',
                'required': 'required'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control select-date',
                'type': 'date',
                'id': 'id_date',
                'required': 'required'
            }),
            'time_slot': forms.Select(attrs={
                'class': 'form-select select-slot',
                'id': 'id_time_slot',
                'required': 'required'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of symptoms, consultation reason, or medical concerns...',
                'required': 'required'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only active doctors available for booking
        self.fields['doctor'].queryset = Doctor.objects.filter(active_status=True)
        # Set minimum date to today
        today_str = timezone.localdate().strftime('%Y-%m-%d')
        self.fields['date'].widget.attrs['min'] = today_str

    def clean_date(self):
        appt_date = self.cleaned_data.get('date')
        if appt_date and appt_date < timezone.localdate():
            raise forms.ValidationError("Appointment date cannot be in the past. Please choose today or a future date.")
        return appt_date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')

        if doctor and date and time_slot:
            # Check for double booking
            existing = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time_slot=time_slot
            ).exclude(status=Appointment.STATUS_CANCELLED)

            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise forms.ValidationError(
                    f"Dr. {doctor.name} already has a confirmed or pending appointment for {time_slot} on {date}. "
                    "Please select another time slot or date."
                )

        return cleaned_data


class AppointmentStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Add internal notes (e.g., confirmed via phone, reschedule requested, etc.)'
            }),
        }


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['diagnosis', 'prescription', 'notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed diagnostic findings and vital observations...',
                'required': 'required'
            }),
            'prescription': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medication names, dosage frequency, duration, precautions...',
                'required': 'required'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dietary guidelines, rest, or follow-up appointment date...'
            }),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['name', 'department', 'specialization', 'consultation_fee', 'available_days', 'active_status', 'room_number', 'email', 'phone', 'experience_years', 'bio']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'available_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Monday, Wednesday, Friday'}),
            'active_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
