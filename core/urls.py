from django.urls import path
from . import admin_views
from .admin_auth import admin_dashboard_secure
from . import views

urlpatterns = [
    path('registration-requests/', admin_views.admin_registration_requests, name='admin_registration_requests'),
    path('registration-process/<int:request_id>/', admin_views.admin_process_registration, name='admin_process_registration'),
    path('change-password/', admin_views.admin_change_password, name='admin_change_password'),
    path('profile/', admin_views.admin_profile, name='admin_profile'),
    path('payment-requests/', admin_views.admin_payment_requests, name='admin_payment_requests'),
    # Admin Dashboard (secure)
    path('', admin_dashboard_secure, name='admin_dashboard'),
    path('dashboard/', admin_dashboard_secure, name='admin_dashboard'),
    
    # Student Management
    path('students/', admin_views.admin_students, name='admin_students'),
    path('students/add/', admin_views.admin_add_student, name='admin_add_student'),
    path('students/<int:student_id>/', admin_views.admin_student_detail, name='admin_student_detail'),
    path('students/<int:student_id>/add-subject/', admin_views.admin_add_subject_to_student, name='admin_add_subject_to_student'),
    
    # Staff Management
    path('staff/', admin_views.admin_staff, name='admin_staff'),
    path('staff/add/', admin_views.admin_add_staff, name='admin_add_staff'),
    path('staff/<int:staff_id>/', admin_views.admin_staff_detail, name='admin_staff_detail'),
    
    # Subjects
    path('subjects/', admin_views.admin_subjects, name='admin_subjects'),
    path('subjects/delete/<int:subject_id>/', admin_views.admin_delete_subject, name='admin_delete_subject'),
    
    # Assignments
    path('assignments/', admin_views.admin_assignments, name='admin_assignments'),
    
    # Events
    path('events/', admin_views.admin_events, name='admin_events'),
    
    # Fees
    path('fees/', admin_views.admin_fees, name='admin_fees'),
    
    # Grades
    path('enrollments/<int:enrollment_id>/add-grade/', admin_views.admin_add_grade, name='admin_add_grade'),
    
    # Upload Profile Picture
    path('upload-picture/', admin_views.admin_upload_picture, name='admin_upload_picture'),
    
    # Assignment Submission (Student)
    path('submit-assignment/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
]
