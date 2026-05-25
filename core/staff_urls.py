from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('my-courses/', views.staff_my_courses, name='staff_my_courses'),
    path('course/<int:subject_id>/students/', views.staff_course_students, name='staff_course_students'),
    path('course/<int:subject_id>/edit-marks/', views.staff_edit_marks, name='staff_edit_marks'),
    path('course/<int:subject_id>/take-attendance/', views.staff_take_attendance, name='staff_take_attendance'),
    path('course/<int:subject_id>/view-attendance/', views.staff_view_attendance, name='staff_view_attendance'),
    path('assignments/', views.staff_assignments, name='staff_assignments'),
    path('assignments/edit/<int:assignment_id>/', views.staff_edit_assignment, name='staff_edit_assignment'),
    path('assignments/delete/<int:assignment_id>/', views.staff_delete_assignment, name='staff_delete_assignment'),
    path('announcements/', views.staff_announcements, name='staff_announcements'),
    path('announcements/edit/<int:announcement_id>/', views.staff_edit_announcement, name='staff_edit_announcement'),
    path('announcements/delete/<int:announcement_id>/', views.staff_delete_announcement, name='staff_delete_announcement'),
    path('submissions/', views.staff_submissions, name='staff_submissions'),
    path('submissions/grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('profile/', views.staff_profile, name='staff_profile'),
    path('change-password/', views.staff_change_password, name='staff_change_password'),
]
