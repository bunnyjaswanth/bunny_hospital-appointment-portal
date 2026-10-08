import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sbj.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from hospital.models import Doctor, Patient, Appointment, MedicalReport, Department


def create_admin_and_sample_data():
    # 1. Create or get Admin Superuser
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@hospital.local')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

    if not User.objects.filter(username=username).exists():
        admin_user = User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Created superuser '{username}' successfully.")
    else:
        admin_user = User.objects.get(username=username)
        print(f"Superuser '{username}' already exists.")

    # 2. Populate Sample Doctors if none exist
    if Doctor.objects.count() == 0:
        print("Populating initial sample doctors...")
        doctors_data = [
            # Cardiology
            {
                'name': 'Dr. Alexander Wright, MD',
                'department': Department.CARDIOLOGY,
                'specialization': 'Interventional Cardiology & Arrhythmia',
                'consultation_fee': 120.00,
                'available_days': 'Monday, Wednesday, Friday',
                'active_status': True,
                'email': 'dr.wright@hospital.local',
                'phone': '+1 (555) 234-5671',
                'room_number': 'Suite 301 - Heart Center',
                'experience_years': 16,
                'avatar_color': 'danger',
                'bio': 'Board-certified cardiologist specializing in coronary interventions, cardiac catheterization, and preventive vascular therapies.'
            },
            {
                'name': 'Dr. Sophia Vance, MD',
                'department': Department.CARDIOLOGY,
                'specialization': 'Echocardiography & Heart Failure',
                'consultation_fee': 110.00,
                'available_days': 'Tuesday, Thursday, Saturday',
                'active_status': True,
                'email': 'dr.vance@hospital.local',
                'phone': '+1 (555) 234-5672',
                'room_number': 'Suite 304 - Heart Center',
                'experience_years': 12,
                'avatar_color': 'danger',
                'bio': 'Expert clinical practitioner focusing on non-invasive imaging, heart failure management, and lipid control.'
            },
            # Pediatrics
            {
                'name': 'Dr. Marcus Thorne, MD',
                'department': Department.PEDIATRICS,
                'specialization': 'General Pediatrics & Neonatal Care',
                'consultation_fee': 85.00,
                'available_days': 'Monday, Tuesday, Thursday, Friday',
                'active_status': True,
                'email': 'dr.thorne@hospital.local',
                'phone': '+1 (555) 345-6781',
                'room_number': 'Room 102 - Children Wing',
                'experience_years': 14,
                'avatar_color': 'warning',
                'bio': 'Dedicated pediatrician with over a decade of compassionate experience in childhood development, immunizations, and pediatric wellness.'
            },
            {
                'name': 'Dr. Chloe Bennett, MD',
                'department': Department.PEDIATRICS,
                'specialization': 'Pediatric Allergy & Pulmonology',
                'consultation_fee': 95.00,
                'available_days': 'Wednesday, Friday, Saturday',
                'active_status': True,
                'email': 'dr.bennett@hospital.local',
                'phone': '+1 (555) 345-6782',
                'room_number': 'Room 106 - Children Wing',
                'experience_years': 9,
                'avatar_color': 'warning',
                'bio': 'Specialist in pediatric asthma, environmental allergies, and childhood respiratory infections.'
            },
            # Orthopedics
            {
                'name': 'Dr. Robert Sterling, MD',
                'department': Department.ORTHOPEDICS,
                'specialization': 'Joint Replacement & Sports Injuries',
                'consultation_fee': 130.00,
                'available_days': 'Monday, Wednesday, Thursday',
                'active_status': True,
                'email': 'dr.sterling@hospital.local',
                'phone': '+1 (555) 456-7891',
                'room_number': 'Suite 405 - Ortho Pavilion',
                'experience_years': 18,
                'avatar_color': 'info',
                'bio': 'Consultant orthopedic surgeon renowned for minimally invasive knee and hip arthroplasty, and athletic ligament reconstruction.'
            },
            {
                'name': 'Dr. Elena Rostova, MD',
                'department': Department.ORTHOPEDICS,
                'specialization': 'Spine Surgery & Trauma Orthopedics',
                'consultation_fee': 140.00,
                'available_days': 'Tuesday, Friday',
                'active_status': True,
                'email': 'dr.rostova@hospital.local',
                'phone': '+1 (555) 456-7892',
                'room_number': 'Suite 408 - Ortho Pavilion',
                'experience_years': 15,
                'avatar_color': 'info',
                'bio': 'Expert spine clinician focusing on cervical spine treatments, disc herniations, and comprehensive physical rehabilitation.'
            },
            # Neurology
            {
                'name': 'Dr. Nathanial Drake, MD, PhD',
                'department': Department.NEUROLOGY,
                'specialization': 'Cognitive Neurology & Epilepsy',
                'consultation_fee': 150.00,
                'available_days': 'Monday, Tuesday, Wednesday, Friday',
                'active_status': True,
                'email': 'dr.drake@hospital.local',
                'phone': '+1 (555) 567-8901',
                'room_number': 'Suite 501 - Neuro Sciences',
                'experience_years': 20,
                'avatar_color': 'primary',
                'bio': 'Academic and clinical neurologist addressing complex seizure disorders, cognitive impairments, and central nervous system therapeutics.'
            },
            {
                'name': 'Dr. Maya Lin, MD',
                'department': Department.NEUROLOGY,
                'specialization': 'Neurovascular & Stroke Care',
                'consultation_fee': 135.00,
                'available_days': 'Wednesday, Thursday, Saturday',
                'active_status': True,
                'email': 'dr.lin@hospital.local',
                'phone': '+1 (555) 567-8902',
                'room_number': 'Suite 503 - Neuro Sciences',
                'experience_years': 11,
                'avatar_color': 'primary',
                'bio': 'Specialist in acute ischemic stroke prevention, transient attacks, and peripheral neuropathy diagnosis.'
            },
        ]

        for d_info in doctors_data:
            Doctor.objects.create(**d_info)
        print(f"Created {len(doctors_data)} doctors.")

    # 3. Create Sample Patients if none exist
    if Patient.objects.count() == 0:
        print("Populating initial sample patients...")
        patients_data = [
            {
                'name': 'Jonathan Reed',
                'email': 'jonathan.reed@example.com',
                'phone': '+1 (555) 789-0123',
                'gender': 'Male',
                'blood_group': 'O+',
                'address': '124 Elmwood Street, Metro City'
            },
            {
                'name': 'Emily Watson',
                'email': 'emily.watson@example.com',
                'phone': '+1 (555) 890-1234',
                'gender': 'Female',
                'blood_group': 'A+',
                'address': '45 Lakeview Terraces, Metro City'
            },
            {
                'name': 'David Kim',
                'email': 'david.kim@example.com',
                'phone': '+1 (555) 901-2345',
                'gender': 'Male',
                'blood_group': 'B-',
                'address': '89 Pinehurst Way, Metro City'
            },
        ]

        for p_info in patients_data:
            Patient.objects.create(**p_info)
        print(f"Created {len(patients_data)} patients.")

    # 4. Create Sample Appointments across all 4 statuses
    if Appointment.objects.count() == 0:
        print("Creating sample appointments with all status badges...")
        doc_cardio = Doctor.objects.filter(department=Department.CARDIOLOGY).first()
        doc_peds = Doctor.objects.filter(department=Department.PEDIATRICS).first()
        doc_ortho = Doctor.objects.filter(department=Department.ORTHOPEDICS).first()
        doc_neuro = Doctor.objects.filter(department=Department.NEUROLOGY).first()

        pat1 = Patient.objects.filter(name='Jonathan Reed').first()
        pat2 = Patient.objects.filter(name='Emily Watson').first()
        pat3 = Patient.objects.filter(name='David Kim').first()

        today = timezone.localdate()

        # 1) Confirmed upcoming appointment
        appt1 = Appointment.objects.create(
            patient=pat1,
            doctor=doc_cardio,
            date=today + timedelta(days=2),
            time_slot='10:00 AM - 10:30 AM',
            reason='Follow-up on mild hypertension and periodic chest heaviness during exercise.',
            status=Appointment.STATUS_CONFIRMED,
            admin_notes='Confirmed by receptionist via phone on schedule check.'
        )

        # 2) Pending review appointment
        appt2 = Appointment.objects.create(
            patient=pat2,
            doctor=doc_peds,
            date=today + timedelta(days=3),
            time_slot='02:30 PM - 03:00 PM',
            reason='Child annual growth milestone evaluation and seasonal allergy review.',
            status=Appointment.STATUS_PENDING
        )

        # 3) Completed appointment with a Medical Report
        appt3 = Appointment.objects.create(
            patient=pat3,
            doctor=doc_ortho,
            date=today - timedelta(days=4),
            time_slot='11:00 AM - 11:30 AM',
            reason='Severe right knee joint pain and swelling following weekend sports session.',
            status=Appointment.STATUS_COMPLETED,
            admin_notes='Completed in clinic. Physical therapy exercises initiated.'
        )

        MedicalReport.objects.create(
            patient=pat3,
            appointment=appt3,
            doctor=doc_ortho,
            diagnosis='Right knee Grade 1 medial collateral ligament (MCL) sprain with mild joint effusion. No meniscal tear on examination.',
            prescription='1. Ibuprofen 400mg with meals twice daily for 5 days\n2. Topical Diclofenac Gel application thrice daily\n3. Cold compression packs 15 mins twice daily',
            notes='Advised 2 weeks rest from contact athletics. Wear hinged neoprene knee sleeve during ambulation. Follow up in 3 weeks if swelling persists.'
        )

        # 4) Cancelled appointment
        appt4 = Appointment.objects.create(
            patient=pat1,
            doctor=doc_neuro,
            date=today - timedelta(days=1),
            time_slot='03:30 PM - 04:00 PM',
            reason='Tension headache consult.',
            status=Appointment.STATUS_CANCELLED,
            admin_notes='Patient requested cancellation due to personal scheduling conflict.'
        )

        print("Created 4 sample appointments across Pending, Confirmed, Completed, and Cancelled statuses.")


if __name__ == '__main__':
    create_admin_and_sample_data()
