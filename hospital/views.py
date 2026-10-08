from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q, Count
import json

from .models import Doctor, Patient, Appointment, MedicalReport, Department
from .forms import (
    AppointmentBookingForm,
    AppointmentStatusUpdateForm,
    MedicalReportForm,
    DoctorForm
)


def home(request):
    """Hospital landing page with statistics, department overview, and doctors."""
    total_doctors = Doctor.objects.filter(active_status=True).count()
    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status=Appointment.STATUS_COMPLETED).count()
    featured_doctors = Doctor.objects.filter(active_status=True)[:6]

    context = {
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'featured_doctors': featured_doctors,
        'departments': [
            {'name': 'Cardiology', 'icon': 'bi-heart-pulse-fill', 'desc': 'Comprehensive heart and cardiovascular diagnostics, prevention, and treatment.'},
            {'name': 'Pediatrics', 'icon': 'bi-emoji-smile-fill', 'desc': 'Specialized infant, child, and adolescent healthcare and developmental tracking.'},
            {'name': 'Orthopedics', 'icon': 'bi-bandaid-fill', 'desc': 'Advanced joint, bone, spine, and musculoskeletal rehabilitation and surgery.'},
            {'name': 'Neurology', 'icon': 'bi-diagram-3-fill', 'desc': 'Expert brain, nerve, and neuro-system diagnostics and clinical therapies.'},
            {'name': 'Dermatology', 'icon': 'bi-sun-fill', 'desc': 'Clinical skin, hair, and aesthetic care with state-of-the-art dermatologic procedures.'},
            {'name': 'General Medicine', 'icon': 'bi-hospital-fill', 'desc': 'Primary outpatient care, wellness checkups, and chronic disease management.'},
        ]
    }
    return render(request, 'hospital/home.html', context)


def doctor_list(request):
    """
    Doctor search and filtering view.
    Supports department filtering (Cardiology, Pediatrics, Orthopedics, Neurology, etc.)
    and keyword search.
    """
    department = request.GET.get('department', '').strip()
    search_query = request.GET.get('q', '').strip()

    doctors = Doctor.objects.all()

    if department and department != 'All':
        doctors = doctors.filter(department=department)

    if search_query:
        doctors = doctors.filter(
            Q(name__icontains=search_query) |
            Q(specialization__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    # Calculate doctor counts per department for filter pills
    dept_counts = {
        'All': Doctor.objects.count(),
        'Cardiology': Doctor.objects.filter(department='Cardiology').count(),
        'Pediatrics': Doctor.objects.filter(department='Pediatrics').count(),
        'Orthopedics': Doctor.objects.filter(department='Orthopedics').count(),
        'Neurology': Doctor.objects.filter(department='Neurology').count(),
        'Dermatology': Doctor.objects.filter(department='Dermatology').count(),
        'General Medicine': Doctor.objects.filter(department='General Medicine').count(),
    }

    context = {
        'doctors': doctors,
        'selected_department': department or 'All',
        'search_query': search_query,
        'dept_counts': dept_counts,
        'all_departments': ['All', 'Cardiology', 'Pediatrics', 'Orthopedics', 'Neurology', 'Dermatology', 'General Medicine'],
    }
    return render(request, 'hospital/doctor_list.html', context)


def book_appointment(request):
    """
    Appointment booking page with interactive slot selection and validation.
    Prevents double booking and past dates.
    """
    doctor_id = request.GET.get('doctor')
    selected_doctor = None
    if doctor_id:
        try:
            selected_doctor = Doctor.objects.get(pk=doctor_id, active_status=True)
        except Doctor.DoesNotExist:
            selected_doctor = None

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            doctor = form.cleaned_data['doctor']
            appt_date = form.cleaned_data['date']
            time_slot = form.cleaned_data['time_slot']
            reason = form.cleaned_data['reason']

            patient_name = form.cleaned_data['patient_name']
            patient_email = form.cleaned_data['patient_email']
            patient_phone = form.cleaned_data['patient_phone']
            patient_gender = form.cleaned_data['patient_gender']
            patient_blood_group = form.cleaned_data['patient_blood_group']

            # Find or create patient record
            patient = Patient.objects.filter(email=patient_email).first()
            if not patient:
                patient = Patient.objects.filter(phone=patient_phone).first()

            if not patient:
                patient = Patient.objects.create(
                    name=patient_name,
                    email=patient_email,
                    phone=patient_phone,
                    gender=patient_gender,
                    blood_group=patient_blood_group,
                    user=request.user if request.user.is_authenticated else None
                )
            else:
                # Update existing patient record with latest details
                patient.name = patient_name
                patient.gender = patient_gender
                if patient_blood_group:
                    patient.blood_group = patient_blood_group
                if request.user.is_authenticated and not patient.user:
                    patient.user = request.user
                patient.save()

            # Create appointment
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=appt_date,
                time_slot=time_slot,
                reason=reason,
                status=Appointment.STATUS_PENDING
            )

            # Store in session for quick access on dashboard
            request.session['last_booked_id'] = appointment.id
            request.session['patient_email'] = patient.email

            messages.success(
                request,
                f"Appointment successfully requested for {patient.name} with {doctor.name} on {appt_date} ({time_slot})!"
            )
            return redirect('appointment_detail', pk=appointment.pk)
        else:
            messages.error(request, "Please correct the errors indicated below.")
    else:
        initial_data = {}
        if selected_doctor:
            initial_data['doctor'] = selected_doctor.id
        if request.user.is_authenticated:
            # Prefill if user has a patient record
            user_patient = Patient.objects.filter(user=request.user).first()
            if user_patient:
                initial_data.update({
                    'patient_name': user_patient.name,
                    'patient_email': user_patient.email,
                    'patient_phone': user_patient.phone,
                    'patient_gender': user_patient.gender,
                    'patient_blood_group': user_patient.blood_group,
                })
            else:
                initial_data.update({
                    'patient_name': request.user.get_full_name() or request.user.username,
                    'patient_email': request.user.email,
                })

        form = AppointmentBookingForm(initial=initial_data)

    doctors = Doctor.objects.filter(active_status=True)
    all_slots = [choice[0] for choice in Appointment.TIME_SLOT_CHOICES]

    context = {
        'form': form,
        'doctors': doctors,
        'selected_doctor': selected_doctor,
        'all_slots': all_slots,
        'today': timezone.localdate().strftime('%Y-%m-%d'),
    }
    return render(request, 'hospital/book_appointment.html', context)


def check_slots_api(request):
    """
    AJAX API endpoint returning booked and available time slots
    for a chosen doctor and date.
    Used by JavaScript for dynamic slot selector.
    """
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Doctor ID and date required.'}, status=400)

    try:
        doctor = Doctor.objects.get(pk=doctor_id)
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found.'}, status=404)

    # Fetch booked slots that are not cancelled
    booked_appointments = Appointment.objects.filter(
        doctor=doctor,
        date=date_str
    ).exclude(status=Appointment.STATUS_CANCELLED)

    booked_slots = list(booked_appointments.values_list('time_slot', flat=True))

    all_slots = [slot[0] for slot in Appointment.TIME_SLOT_CHOICES]
    available_slots = [slot for slot in all_slots if slot not in booked_slots]

    return JsonResponse({
        'doctor_name': doctor.name,
        'doctor_department': doctor.department,
        'consultation_fee': str(doctor.consultation_fee),
        'available_days': doctor.available_days,
        'room_number': doctor.room_number,
        'date': date_str,
        'all_slots': all_slots,
        'booked_slots': booked_slots,
        'available_slots': available_slots,
    })


def appointment_detail(request, pk):
    """View single appointment confirmation and details."""
    appointment = get_object_or_404(Appointment, pk=pk)
    report = getattr(appointment, 'medical_report', None)

    context = {
        'appointment': appointment,
        'report': report,
    }
    return render(request, 'hospital/appointment_detail.html', context)


def patient_dashboard(request):
    """
    Patient dashboard showing upcoming and past appointments.
    Patients can search by their email/phone or view linked account appointments.
    """
    query = request.GET.get('search', '').strip()
    session_email = request.session.get('patient_email', '')

    appointments = Appointment.objects.none()
    current_patient = None

    if request.user.is_authenticated and not request.user.is_staff:
        # User is logged in as patient
        patient_obj = Patient.objects.filter(user=request.user).first()
        if patient_obj:
            current_patient = patient_obj
            appointments = Appointment.objects.filter(patient=patient_obj)
        else:
            appointments = Appointment.objects.filter(patient__email=request.user.email)

    if not appointments.exists() and query:
        appointments = Appointment.objects.filter(
            Q(patient__email__iexact=query) | Q(patient__phone__icontains=query)
        )
        if appointments.exists():
            current_patient = appointments.first().patient
            request.session['patient_email'] = current_patient.email
    elif not appointments.exists() and session_email:
        appointments = Appointment.objects.filter(patient__email__iexact=session_email)
        if appointments.exists():
            current_patient = appointments.first().patient

    # If still empty and user is staff or admin, show all for convenience or guidance
    today = timezone.localdate()
    upcoming_appointments = appointments.filter(date__gte=today).exclude(status=Appointment.STATUS_CANCELLED).order_by('date', 'time_slot')
    past_appointments = appointments.filter(Q(date__lt=today) | Q(status__in=[Appointment.STATUS_COMPLETED, Appointment.STATUS_CANCELLED])).order_by('-date', 'time_slot')

    # Metrics
    stats = {
        'total': appointments.count(),
        'pending': appointments.filter(status=Appointment.STATUS_PENDING).count(),
        'confirmed': appointments.filter(status=Appointment.STATUS_CONFIRMED).count(),
        'completed': appointments.filter(status=Appointment.STATUS_COMPLETED).count(),
        'cancelled': appointments.filter(status=Appointment.STATUS_CANCELLED).count(),
    }

    context = {
        'patient': current_patient,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'stats': stats,
        'query': query,
    }
    return render(request, 'hospital/patient_dashboard.html', context)


@require_POST
def cancel_appointment(request, pk):
    """Patient or staff action to cancel an appointment."""
    appointment = get_object_or_404(Appointment, pk=pk)

    if appointment.status == Appointment.STATUS_COMPLETED:
        messages.error(request, "Completed appointments cannot be cancelled.")
        return redirect('appointment_detail', pk=pk)

    appointment.status = Appointment.STATUS_CANCELLED
    appointment.admin_notes = (appointment.admin_notes or "") + f"\nCancelled by user on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    appointment.save()

    messages.warning(request, f"Appointment #{appointment.id} has been cancelled.")
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('appointment_detail', pk=pk)


# ==================== ADMIN & STAFF WORKFLOWS ====================

def is_staff_member(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(is_staff_member, login_url='/login/?next=/staff/appointments/')
def staff_appointments(request):
    """
    Admin and Staff appointment management view.
    Manage schedules, filter by status or doctor, confirm or cancel appointments.
    """
    status_filter = request.GET.get('status', 'All')
    doctor_filter = request.GET.get('doctor', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('q', '').strip()

    appointments = Appointment.objects.select_related('patient', 'doctor').all()

    if status_filter and status_filter != 'All':
        appointments = appointments.filter(status=status_filter)

    if doctor_filter:
        appointments = appointments.filter(doctor_id=doctor_filter)

    if date_filter:
        appointments = appointments.filter(date=date_filter)

    if search_query:
        appointments = appointments.filter(
            Q(patient__name__icontains=search_query) |
            Q(patient__phone__icontains=search_query) |
            Q(patient__email__icontains=search_query) |
            Q(doctor__name__icontains=search_query) |
            Q(reason__icontains=search_query)
        )

    # Metric counts for admin dashboard
    today = timezone.localdate()
    stats = {
        'all': Appointment.objects.count(),
        'pending': Appointment.objects.filter(status=Appointment.STATUS_PENDING).count(),
        'confirmed': Appointment.objects.filter(status=Appointment.STATUS_CONFIRMED).count(),
        'completed': Appointment.objects.filter(status=Appointment.STATUS_COMPLETED).count(),
        'cancelled': Appointment.objects.filter(status=Appointment.STATUS_CANCELLED).count(),
        'today': Appointment.objects.filter(date=today).count(),
    }

    doctors = Doctor.objects.all()

    context = {
        'appointments': appointments,
        'doctors': doctors,
        'stats': stats,
        'current_status': status_filter,
        'selected_doctor': doctor_filter,
        'selected_date': date_filter,
        'search_query': search_query,
    }
    return render(request, 'hospital/staff_appointments.html', context)


@require_POST
@user_passes_test(is_staff_member, login_url='/login/')
def update_appointment_status(request, pk):
    """Quick AJAX or form action for staff to change appointment status."""
    appointment = get_object_or_404(Appointment, pk=pk)
    new_status = request.POST.get('status')
    admin_notes = request.POST.get('admin_notes', '')

    valid_statuses = [choice[0] for choice in Appointment.STATUS_CHOICES]
    if new_status in valid_statuses:
        appointment.status = new_status
        if admin_notes:
            appointment.admin_notes = admin_notes
        appointment.save()
        messages.success(request, f"Appointment #{appointment.id} updated to '{new_status}'.")
    else:
        messages.error(request, "Invalid status choice provided.")

    return redirect('staff_appointments')


@user_passes_test(is_staff_member, login_url='/login/')
def manage_medical_report(request, pk):
    """Staff or Doctor view to create or edit medical report for an appointment."""
    appointment = get_object_or_404(Appointment, pk=pk)
    report = getattr(appointment, 'medical_report', None)

    if request.method == 'POST':
        form = MedicalReportForm(request.POST, instance=report)
        if form.is_valid():
            report_obj = form.save(commit=False)
            report_obj.appointment = appointment
            report_obj.patient = appointment.patient
            report_obj.doctor = appointment.doctor
            report_obj.save()

            # Mark appointment as completed if not already
            if appointment.status != Appointment.STATUS_COMPLETED:
                appointment.status = Appointment.STATUS_COMPLETED
                appointment.save()

            messages.success(request, f"Medical consultation report saved for appointment #{appointment.id}.")
            return redirect('appointment_detail', pk=appointment.id)
    else:
        form = MedicalReportForm(instance=report)

    context = {
        'form': form,
        'appointment': appointment,
        'report': report,
    }
    return render(request, 'hospital/medical_report_form.html', context)


@user_passes_test(is_staff_member, login_url='/login/')
def staff_doctors(request):
    """Staff dashboard to view, add, or toggle doctors."""
    doctors = Doctor.objects.all().order_by('department', 'name')
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Doctor {doctor.name} added successfully.")
            return redirect('staff_doctors')
    else:
        form = DoctorForm()

    context = {
        'doctors': doctors,
        'form': form,
    }
    return render(request, 'hospital/staff_doctors.html', context)


@require_POST
@user_passes_test(is_staff_member, login_url='/login/')
def toggle_doctor_status(request, pk):
    """Toggle doctor active status."""
    doctor = get_object_or_404(Doctor, pk=pk)
    doctor.active_status = not doctor.active_status
    doctor.save()
    status_str = "Active" if doctor.active_status else "Inactive"
    messages.info(request, f"Status for {doctor.name} set to {status_str}.")
    return redirect('staff_doctors')


# ==================== AUTHENTICATION VIEWS ====================

def user_login(request):
    """Custom login view for patients and staff."""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('staff_appointments')
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_staff:
                return redirect('staff_appointments')
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, 'hospital/login.html', context)


def user_register(request):
    """Registration for new patients."""
    if request.user.is_authenticated:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Link or create Patient object
            Patient.objects.get_or_create(
                user=user,
                defaults={
                    'name': user.username,
                    'email': user.email or f"{user.username}@hospital.local",
                    'phone': 'N/A'
                }
            )
            messages.success(request, "Account created successfully! Welcome to Medicare Hospital Portal.")
            return redirect('patient_dashboard')
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'hospital/register.html', context)


def user_logout(request):
    """Logout view."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')
