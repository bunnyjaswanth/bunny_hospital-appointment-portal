from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from hospital.models import Doctor, Patient, Appointment, MedicalReport, Department


class HospitalPortalTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create doctor
        self.doctor = Doctor.objects.create(
            name="Dr. Test Cardiologist",
            department=Department.CARDIOLOGY,
            specialization="Preventive Cardiology",
            consultation_fee=100.00,
            available_days="Mon, Wed, Fri",
            active_status=True,
            room_number="Room 101"
        )

        self.doctor_ortho = Doctor.objects.create(
            name="Dr. Test Ortho",
            department=Department.ORTHOPEDICS,
            specialization="Knee Specialist",
            consultation_fee=120.00,
            available_days="Tue, Thu",
            active_status=True,
            room_number="Room 201"
        )

        # Create patient
        self.patient = Patient.objects.create(
            name="Jane Patient",
            email="jane@example.com",
            phone="+1555123456",
            gender="Female",
            blood_group="O+"
        )

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            email="admintest@example.com",
            password="testpassword123"
        )

        self.future_date = timezone.localdate() + timedelta(days=2)
        self.time_slot = "10:00 AM - 10:30 AM"

    def test_home_page_loads(self):
        """Test home page status code and content."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MediCare+")
        self.assertContains(response, "Cardiology")

    def test_doctor_filter_by_department(self):
        """Test doctor search and department filtering."""
        # Filter Cardiology
        response = self.client.get(reverse('doctor_list') + '?department=Cardiology')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Test Cardiologist")
        self.assertNotContains(response, "Dr. Test Ortho")

        # Filter Orthopedics
        response = self.client.get(reverse('doctor_list') + '?department=Orthopedics')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dr. Test Ortho")
        self.assertNotContains(response, "Dr. Test Cardiologist")

    def test_interactive_slots_api(self):
        """Test /api/slots/ returns booked and available slots."""
        # Book a slot first
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=self.future_date,
            time_slot=self.time_slot,
            reason="Chest checkup",
            status=Appointment.STATUS_CONFIRMED
        )

        # Call API
        url = reverse('check_slots_api') + f'?doctor_id={self.doctor.id}&date={self.future_date}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn(self.time_slot, data['booked_slots'])
        self.assertNotIn(self.time_slot, data['available_slots'])
        self.assertEqual(data['doctor_name'], self.doctor.name)

    def test_prevent_double_booking(self):
        """Test that double booking for same doctor, date and slot is prevented."""
        # First booking succeeds
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=self.future_date,
            time_slot=self.time_slot,
            reason="Initial booking",
            status=Appointment.STATUS_PENDING
        )

        # Attempt to book the same doctor, date, and slot
        post_data = {
            'doctor': self.doctor.id,
            'date': self.future_date.strftime('%Y-%m-%d'),
            'time_slot': self.time_slot,
            'reason': "Second booking attempt",
            'patient_name': "Another Patient",
            'patient_email': "another@example.com",
            'patient_phone': "+1555987654",
            'patient_gender': "Male",
            'patient_blood_group': "A+",
        }
        response = self.client.post(reverse('book_appointment'), post_data)
        # Should re-render form with error message (status 200, not redirect)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already has a confirmed or pending appointment")

        # Total appointments should still be 1
        self.assertEqual(Appointment.objects.filter(doctor=self.doctor, date=self.future_date).count(), 1)

    def test_prevent_past_date_booking(self):
        """Test that booking for past dates is rejected."""
        past_date = timezone.localdate() - timedelta(days=2)
        post_data = {
            'doctor': self.doctor.id,
            'date': past_date.strftime('%Y-%m-%d'),
            'time_slot': self.time_slot,
            'reason': "Past booking",
            'patient_name': "Jane Patient",
            'patient_email': "jane@example.com",
            'patient_phone': "+1555123456",
            'patient_gender': "Female",
        }
        response = self.client.post(reverse('book_appointment'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot be in the past")

    def test_successful_booking_and_redirect(self):
        """Test valid appointment creation."""
        post_data = {
            'doctor': self.doctor.id,
            'date': self.future_date.strftime('%Y-%m-%d'),
            'time_slot': "02:00 PM - 02:30 PM",
            'reason': "Routine heart checkup",
            'patient_name': "New Patient",
            'patient_email': "new@example.com",
            'patient_phone': "+1555888999",
            'patient_gender': "Male",
            'patient_blood_group': "B+",
        }
        response = self.client.post(reverse('book_appointment'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirects to appointment_detail
        self.assertTrue(Appointment.objects.filter(reason="Routine heart checkup").exists())

    def test_staff_status_update_workflow(self):
        """Test admin / staff can confirm, complete, or cancel appointments."""
        self.client.force_login(self.admin_user)

        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=self.future_date,
            time_slot="11:00 AM - 11:30 AM",
            reason="Checkup",
            status=Appointment.STATUS_PENDING
        )

        # 1. Confirm appointment
        response = self.client.post(
            reverse('update_appointment_status', args=[appt.id]),
            {'status': 'Confirmed'}
        )
        self.assertEqual(response.status_code, 302)
        appt.refresh_from_db()
        self.assertEqual(appt.status, Appointment.STATUS_CONFIRMED)

        # 2. Add Medical Report & Complete
        report_url = reverse('manage_medical_report', args=[appt.id])
        report_data = {
            'diagnosis': 'Healthy cardiac rhythm with normal ECG.',
            'prescription': 'No medications required. Maintain regular cardio exercise.',
            'notes': 'Follow up in 6 months.'
        }
        response = self.client.post(report_url, report_data)
        self.assertEqual(response.status_code, 302)

        appt.refresh_from_db()
        self.assertEqual(appt.status, Appointment.STATUS_COMPLETED)
        self.assertTrue(hasattr(appt, 'medical_report'))
        self.assertEqual(appt.medical_report.diagnosis, 'Healthy cardiac rhythm with normal ECG.')
