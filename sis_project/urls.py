from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views
from core.admin_auth import admin_login_view

urlpatterns = [
    path('register/', views.student_register, name='register'),
    path('admin/', admin.site.urls),
    path('admin-login/', admin_login_view, name='admin_login'),
    path('custom-admin/', include('core.urls')),
    path('staff/', include('core.staff_urls')),
    
    # Redirects for old admin URLs
    path('admin-dashboard/', views.redirect_to_admin_dashboard, name='redirect_admin_dashboard'),
    path('admin-students/', views.redirect_to_admin_students, name='redirect_admin_students'),
    path('admin-subjects/', views.redirect_to_admin_subjects, name='redirect_admin_subjects'),
    path('admin-assignments/', views.redirect_to_admin_assignments, name='redirect_admin_assignments'),
    path('admin-events/', views.redirect_to_admin_events, name='redirect_admin_events'),
    path('admin-fees/', views.redirect_to_admin_fees, name='redirect_admin_fees'),
    
    # Main site URLs
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile_view'),
    path('my-subjects/', views.my_subjects, name='my_subjects'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('my-marks/', views.my_marks, name='my_marks'),
    path('my-attendance/', views.my_attendance, name='my_attendance'),
    path('my-fee/', views.my_fee, name='my_fee'),
    path('upcoming-events/', views.upcoming_events, name='upcoming_events'),
    path('change-password/', views.change_password, name='change_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('pay-fee/<int:fee_id>/', views.pay_fee, name='pay_fee'),
    path('submit-assignment/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    
    # Student Announcements
    path('student-announcements/', views.student_announcements, name='student_announcements'),
    path('mark-announcement-read/<int:announcement_id>/', views.mark_announcement_read, name='mark_announcement_read'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
