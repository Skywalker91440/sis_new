from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

def login_view(request):
    """Student login view"""
    from django.shortcuts import render, redirect
    from django.contrib.auth import authenticate, login
    from django.contrib import messages
    from .models import StudentProfile, StaffProfile
    
    if request.user.is_authenticated:
        # Redirect based on user type
        if hasattr(request.user, 'student_profile'):
            return redirect('dashboard')
        elif hasattr(request.user, 'staff_profile'):
            return redirect('staff_dashboard')
        elif request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        login_id = request.POST.get('username')
        password = request.POST.get('password')
        
        # First try to authenticate with username
        user = authenticate(request, username=login_id, password=password)
        
        # If not found, try to find user by student_id
        if not user:
            try:
                student = StudentProfile.objects.get(student_id=login_id)
                user = student.user
                if not user.check_password(password):
                    user = None
            except StudentProfile.DoesNotExist:
                pass
        
        # If still not found, try staff_id
        if not user:
            try:
                staff = StaffProfile.objects.get(staff_id=login_id)
                user = staff.user
                if not user.check_password(password):
                    user = None
            except StaffProfile.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect based on user type - STUDENT goes to dashboard
            if hasattr(user, 'student_profile'):
                return redirect('dashboard')
            elif hasattr(user, 'staff_profile'):
                return redirect('staff_dashboard')
            elif user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Student ID/Username or Password')
    
    return render(request, 'login.html')


def submit_assignment(request, assignment_id):
    """Handle assignment submission"""
    from django.shortcuts import get_object_or_404, render, redirect
    from django.contrib import messages
    from django.utils import timezone
    from django.contrib.auth.decorators import login_required
    from .models import Assignment, AssignmentSubmission, StudentProfile, StudentAssignment
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login first')
        return redirect('login')
    
    if not hasattr(request.user, 'student_profile'):
        messages.warning(request, 'Access denied. Student only.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = request.user.student_profile
    
    # Check if student is enrolled in this subject
    if not student.subjects.filter(subject=assignment.subject).exists():
        messages.error(request, 'You are not enrolled in this course')
        return redirect('my_tasks')
    
    # Get or create submission
    submission, created = AssignmentSubmission.objects.get_or_create(
        student=student,
        assignment=assignment
    )
    
    if request.method == 'POST':
        submission_file = request.FILES.get('submission_file')
        submission_text = request.POST.get('submission_text', '')
        
        if submission_file or submission_text:
            if submission_file:
                submission.file = submission_file
            if submission_text:
                submission.submission_text = submission_text
            submission.submitted_at = timezone.now()
            submission.status = 'Submitted'
            submission.save()
            
            # Update StudentAssignment status
            student_assignment, _ = StudentAssignment.objects.get_or_create(
                student=student,
                assignment=assignment
            )
            student_assignment.status = 'Submitted'
            student_assignment.save()
            
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('my_tasks')
        else:
            messages.error(request, 'Please provide a file or text submission')
    
    context = {
        'assignment': assignment,
        'submission': submission,
        'student': student,
    }
    return render(request, 'submit_assignment.html', context)


def redirect_to_admin_dashboard(request):
    """Redirect to admin dashboard"""
    from django.shortcuts import redirect
    return redirect('admin_dashboard')

def admin_dashboard(request):
    """Admin dashboard view"""
    from django.shortcuts import render
    return render(request, 'core/admin_dashboard.html', {})

def manage_courses(request):
    """Manage courses view"""
    from django.shortcuts import render
    return render(request, 'core/manage_courses.html', {})

def manage_users(request):
    """Manage users view"""
    from django.shortcuts import render
    return render(request, 'core/manage_users.html', {})

def manage_assignments(request):
    """Manage assignments view"""
    from django.shortcuts import render
    return render(request, 'core/manage_assignments.html', {})

def view_submissions(request):
    """View submissions view"""
    from django.shortcuts import render
    return render(request, 'core/view_submissions.html', {})

def assignment_detail(request, assignment_id):
    """Assignment detail view"""
    from django.shortcuts import get_object_or_404, render
    from .models import Assignment
    assignment = get_object_or_404(Assignment, id=assignment_id)
    return render(request, 'core/assignment_detail.html', {'assignment': assignment})

def course_detail(request, course_id):
    """Course detail view"""
    from django.shortcuts import get_object_or_404, render
    from .models import Course
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'core/course_detail.html', {'course': course})


def admin_add_subject_to_student(request, *args, **kwargs):
    """Auto-generated view for admin_add_subject_to_student"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_assignments(request, *args, **kwargs):
    """Auto-generated view for admin_assignments"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_staff_detail(request, *args, **kwargs):
    """Auto-generated view for admin_staff_detail"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_staff(request, *args, **kwargs):
    """Auto-generated view for admin_staff"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_student_detail(request, *args, **kwargs):
    """Auto-generated view for admin_student_detail"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_add_staff(request, *args, **kwargs):
    """Auto-generated view for admin_add_staff"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_fees(request, *args, **kwargs):
    """Auto-generated view for admin_fees"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_students(request, *args, **kwargs):
    """Auto-generated view for admin_students"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_add_student(request, *args, **kwargs):
    """Auto-generated view for admin_add_student"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_upload_picture(request, *args, **kwargs):
    """Auto-generated view for admin_upload_picture"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_delete_subject(request, *args, **kwargs):
    """Auto-generated view for admin_delete_subject"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_subjects(request, *args, **kwargs):
    """Auto-generated view for admin_subjects"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_add_grade(request, *args, **kwargs):
    """Auto-generated view for admin_add_grade"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")


def admin_events(request, *args, **kwargs):
    """Auto-generated view for admin_events"""
    from django.shortcuts import render
    from django.http import HttpResponse
    
    # Check if this view expects parameters
    if args or kwargs:
        return HttpResponse(f"{view} page - Parameters received: {kwargs}")
    else:
        return HttpResponse(f"{view} page - Coming soon!")

def redirect_to_admin_students(request):
    """Redirect to admin students page"""
    from django.shortcuts import redirect
    return redirect('admin_students')

def admin_students(request):
    """Admin students management view"""
    from django.http import HttpResponse
    return HttpResponse("Admin Students Page - Coming soon!")

# ============ ADDED MISSING VIEWS ============

def home(request):
    from django.shortcuts import render
    return render(request, 'home.html', {})

def dashboard(request):
    """Student dashboard view - matches template requirements"""
    from django.shortcuts import render
    from django.contrib import messages
    from django.shortcuts import redirect
    from .models import StudentProfile, StudentSubject, StudentAnnouncement, StudentAttendance, StudentAssignment
    from datetime import date
    
    # Check if user is logged in
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login first')
        return redirect('login')
    
    # Check if user is a student
    if not hasattr(request.user, 'student_profile'):
        messages.warning(request, 'Access denied. Student only area.')
        return redirect('login')
    
    student = request.user.student_profile
    
    # Get enrolled subjects
    enrollments = StudentSubject.objects.filter(student=student)
    total_courses = enrollments.count()
    
    # Get pending assignments (tasks)
    pending_assignments = StudentAssignment.objects.filter(
        student=student,
        status='Pending'
    )
    pending_tasks = pending_assignments.count()
    
    # Get recent announcements
    recent_announcements = StudentAnnouncement.objects.filter(
        student=student
    ).select_related('announcement').order_by('-announcement__created_date')[:5]
    
    # Calculate attendance
    attendances = StudentAttendance.objects.filter(student=student)
    total_attendance = attendances.count()
    present_count = attendances.filter(status='present').count()
    attendance_percent = int((present_count / total_attendance * 100)) if total_attendance > 0 else 0
    
    context = {
        'total_courses': total_courses,
        'pending_tasks': pending_tasks,
        'total_announcements': recent_announcements.count(),
        'attendance': attendance_percent,
        'recent_announcements': recent_announcements,
        'student': student,
        'user': request.user,
    }
    return render(request, 'dashboard.html', context)


def change_password(request):
    """Change password view"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth.decorators import login_required
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile_view')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})



def forgot_password(request):
    """Forgot password view - send reset link to email"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from django.contrib.auth.models import User
    from django.core.mail import send_mail
    from django.conf import settings
    import random
    import string
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate a random temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # Set temporary password
            user.set_password(temp_password)
            user.save()
            
            # Send email with temporary password
            try:
                send_mail(
                    subject='Password Reset - SIS Tanzania',
                    message=f"""
Dear {user.get_full_name() or user.username},

You requested to reset your password.

Here is your temporary password:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 Temporary Password: {temp_password}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please login using this temporary password and change your password immediately.

Login link: http://127.0.0.1:8002/login/

For security reasons, we recommend changing your password after logging in.

If you did not request this password reset, please ignore this email.

Best regards,
SIS Tanzania Administration
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, f'Password reset link has been sent to {email}. Please check your email.')
            except Exception as e:
                messages.error(request, f'Failed to send email. Please try again later.')
                
        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
        
        return redirect('forgot_password')
    
    return render(request, 'forgot_password.html')





def signup_view(request):
    from django.shortcuts import render
    return render(request, 'core/signup.html', {})

def profile_view(request):
    """User profile view"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from django.contrib.auth.decorators import login_required
    from .models import UserProfile
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Handle POST request for updating profile
    if request.method == 'POST':
        # Update phone
        if 'phone' in request.POST:
            phone = request.POST.get('phone')
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.phone = phone
            profile.save()
            messages.success(request, 'Phone number updated successfully!')
        
        # Update department and year for students
        elif 'department' in request.POST or 'year' in request.POST:
            if hasattr(request.user, 'student_profile'):
                student = request.user.student_profile
                if 'department' in request.POST:
                    student.department = request.POST.get('department')
                if 'year' in request.POST:
                    student.year = request.POST.get('year')
                student.save()
                messages.success(request, 'Academic information updated successfully!')
        
        # Handle profile picture upload
        elif 'profile_picture' in request.FILES:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            messages.success(request, 'Profile picture updated successfully!')
        
        return redirect('profile_view')
    
    context = {
        'user': request.user,
    }
    
    # Add student specific data if user is student
    if hasattr(request.user, 'student_profile'):
        context['student'] = request.user.student_profile
        context['student_profile'] = request.user.student_profile
        context['user_type'] = 'student'
    
    # Add staff specific data if user is staff
    elif hasattr(request.user, 'staff_profile'):
        context['staff'] = request.user.staff_profile
        context['user_type'] = 'staff'
    
    return render(request, 'profile.html', context)


def my_subjects(request):
    """Student subjects view - shows all enrolled subjects with grades"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from django.contrib.auth.decorators import login_required
    from .models import StudentSubject
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login first')
        return redirect('login')
    
    # Check if user is a student
    if not hasattr(request.user, 'student_profile'):
        messages.warning(request, 'Access denied. Student only area.')
        return redirect('dashboard')
    
    student = request.user.student_profile
    
    # Get all subjects enrolled by this student with grades
    student_subjects = StudentSubject.objects.filter(student=student).select_related('subject')
    
    # Also get the instructor name for each subject
    for ss in student_subjects:
        if ss.subject.instructor:
            ss.instructor_name = ss.subject.instructor.user.get_full_name() or ss.subject.instructor.user.username
        else:
            ss.instructor_name = 'Not Assigned'
    
    context = {
        'student_subjects': student_subjects,
        'student': student,
    }
    return render(request, 'my_subjects.html', context)


def my_attendance(request):
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from .models import StudentAttendance, StudentSubject
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not hasattr(request.user, 'student_profile'):
        return redirect('dashboard')
    
    student = request.user.student_profile
    enrollments = StudentSubject.objects.filter(student=student).select_related('subject')
    
    attendance_data = []
    for enrollment in enrollments:
        subject = enrollment.subject
        attendances = StudentAttendance.objects.filter(student=student, subject=subject)
        total = attendances.count()
        present = attendances.filter(status='present').count()
        percent = int((present / total * 100)) if total > 0 else 0
        
        attendance_data.append({
            'code': subject.code,
            'name': subject.name,
            'total': total,
            'present': present,
            'absent': total - present,
            'percent': percent,
        })
    
    return render(request, 'my_attendance.html', {'attendance_data': attendance_data})


def my_marks(request):
    from django.shortcuts import render, redirect
    from .models import StudentSubject
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not hasattr(request.user, 'student_profile'):
        return redirect('dashboard')
    
    student = request.user.student_profile
    enrollments = StudentSubject.objects.filter(student=student).select_related('subject')
    
    subjects_with_marks = []
    for enrollment in enrollments:
        subjects_with_marks.append({
            'code': enrollment.subject.code,
            'name': enrollment.subject.name,
            'credits': enrollment.subject.credits,
            'grade': enrollment.grade,
        })
    
    return render(request, 'my_marks.html', {'subjects_with_marks': subjects_with_marks})


def my_fee(request):
    from django.shortcuts import render, redirect
    from .models import StudentFee
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not hasattr(request.user, 'student_profile'):
        return redirect('dashboard')
    
    student = request.user.student_profile
    fees = StudentFee.objects.filter(student=student)
    
    return render(request, 'my_fee.html', {'fees': fees})


def my_tasks(request):
    """Student tasks/assignments view"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from django.contrib.auth.decorators import login_required
    from django.utils import timezone
    from datetime import date
    from .models import StudentAssignment
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login first')
        return redirect('login')
    
    # Check if user is a student
    if not hasattr(request.user, 'student_profile'):
        messages.warning(request, 'Access denied. Student only area.')
        return redirect('dashboard')
    
    student = request.user.student_profile
    
    # Get all assignments for this student
    student_assignments = StudentAssignment.objects.filter(student=student).select_related('assignment__subject')
    
    # Calculate statistics
    total_assignments = student_assignments.count()
    pending_count = student_assignments.filter(status='Pending').count()
    submitted_count = student_assignments.filter(status='Submitted').count()
    graded_count = student_assignments.filter(status='Graded').count()
    
    context = {
        'student_assignments': student_assignments,
        'total_assignments': total_assignments,
        'pending_count': pending_count,
        'submitted_count': submitted_count,
        'graded_count': graded_count,
        'today': date.today(),
    }
    return render(request, 'my_tasks.html', context)


def student_announcements(request):
    """Student announcements view"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from .models import StudentAnnouncement
    
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login first')
        return redirect('login')
    
    if not hasattr(request.user, 'student_profile'):
        messages.warning(request, 'Access denied. Student only area.')
        return redirect('dashboard')
    
    student = request.user.student_profile
    
    # Get all announcements for this student
    announcements = StudentAnnouncement.objects.filter(
        student=student
    ).select_related('announcement').order_by('-announcement__created_date')
    
    context = {
        'announcements': announcements,
        'total_count': announcements.count(),
        'unread_count': announcements.filter(is_read=False).count(),
    }
    return render(request, 'student_announcements.html', context)


def upcoming_events(request):
    from django.http import HttpResponse
    return HttpResponse("Upcoming Events Page - Coming soon!")





@login_required
def mark_announcement_read(request, announcement_id):
    """Mark announcement as read"""
    from django.http import JsonResponse
    from django.utils import timezone
    from .models import StudentAnnouncement
    
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
    
    if not hasattr(request.user, 'student_profile'):
        return JsonResponse({'status': 'error', 'message': 'Student only'}, status=403)
    
    try:
        student_ann = StudentAnnouncement.objects.get(
            student=request.user.student_profile,
            announcement_id=announcement_id
        )
        student_ann.is_read = True
        student_ann.read_at = timezone.now()
        student_ann.save()
        return JsonResponse({'status': 'success', 'message': 'Marked as read'})
    except StudentAnnouncement.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Announcement not found'}, status=404)


def redirect_to_admin_assignments(request):
    from django.shortcuts import redirect
    return redirect('admin_assignments')

def redirect_to_admin_events(request):
    from django.shortcuts import redirect
    return redirect('admin_events')

def redirect_to_admin_fees(request):
    from django.shortcuts import redirect
    return redirect('admin_fees')

def redirect_to_admin_subjects(request):
    from django.shortcuts import redirect
    return redirect('admin_subjects')

def staff_change_password(request):
    """Staff change password view"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth.decorators import login_required
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check if user is staff
    if not hasattr(request.user, 'staff_profile') and not request.user.is_staff:
        messages.warning(request, 'Access denied. Staff only area.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated! Please login again.')
            from django.contrib.auth import logout
            logout(request)
            return redirect('login')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'staff/change_password.html', {'form': form})

# ==================== STAFF VIEWS ====================

def staff_dashboard(request):
    """Staff dashboard view"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from django.contrib.auth.decorators import login_required
    from .models import StaffProfile, Subject, Assignment, Announcement
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not hasattr(request.user, 'staff_profile'):
        messages.warning(request, 'Access denied. Staff only area.')
        return redirect('dashboard')
    
    staff = request.user.staff_profile
    subjects = staff.subjects.all()
    
    # Calculate statistics
    total_students = 0
    for subject in subjects:
        total_students += subject.students.count()
    
    total_assignments = Assignment.objects.filter(subject__in=subjects).count()
    total_announcements = Announcement.objects.filter(staff=staff).count()
    
    context = {
        'staff': staff,
        'subjects': subjects,
        'total_students': total_students,
        'total_assignments': total_assignments,
        'total_announcements': total_announcements,
    }
    return render(request, 'staff/dashboard.html', context)

def staff_my_courses(request):
    """Staff my courses view"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not hasattr(request.user, 'staff_profile'):
        messages.warning(request, 'Access denied. Staff only area.')
        return redirect('dashboard')
    
    staff = request.user.staff_profile
    subjects = staff.subjects.all()
    return render(request, 'staff/my_courses.html', {'subjects': subjects})

def staff_course_students(request, subject_id):
    """View students in a course"""
    from django.shortcuts import render, get_object_or_404, redirect
    from django.contrib import messages
    from .models import Subject, StudentSubject
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    subject = get_object_or_404(Subject, id=subject_id)
    students = StudentSubject.objects.filter(subject=subject).select_related('student')
    
    return render(request, 'staff/course_students.html', {
        'subject': subject,
        'students': students
    })

def staff_edit_marks(request, subject_id):
    """Edit student marks"""
    from django.shortcuts import render, get_object_or_404, redirect
    from django.contrib import messages
    from .models import Subject, StudentSubject
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('mark_'):
                enrollment_id = key.split('_')[1]
                enrollment = get_object_or_404(StudentSubject, id=enrollment_id)
                enrollment.grade = value
                enrollment.save()
        messages.success(request, 'Marks updated successfully!')
        return redirect('staff_course_students', subject_id=subject_id)
    
    students = StudentSubject.objects.filter(subject=subject).select_related('student')
    
    return render(request, 'staff/edit_marks.html', {
        'subject': subject,
        'students': students
    })

def staff_take_attendance(request, subject_id):
    """Take attendance for a course"""
    from django.shortcuts import render, get_object_or_404, redirect
    from django.contrib import messages
    from django.utils import timezone
    from .models import Subject, StudentSubject, StudentAttendance
    from datetime import date
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    subject = get_object_or_404(Subject, id=subject_id)
    students = StudentSubject.objects.filter(subject=subject).select_related('student')
    
    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date', date.today())
        
        for enrollment in students:
            status = request.POST.get(f'attendance_{enrollment.id}')
            if status:
                StudentAttendance.objects.update_or_create(
                    student=enrollment.student,
                    subject=subject,
                    date=attendance_date,
                    defaults={'status': status}
                )
        messages.success(request, 'Attendance saved successfully!')
        return redirect('staff_take_attendance', subject_id=subject_id)
    
    return render(request, 'staff/take_attendance.html', {
        'subject': subject,
        'students': students,
        'today': date.today()
    })

def staff_view_attendance(request, subject_id):
    """View attendance records"""
    from django.shortcuts import render, get_object_or_404
    from .models import Subject, StudentSubject, StudentAttendance
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    subject = get_object_or_404(Subject, id=subject_id)
    students = StudentSubject.objects.filter(subject=subject).select_related('student')
    
    student_stats = []
    for enrollment in students:
        student = enrollment.student
        attendances = StudentAttendance.objects.filter(student=student, subject=subject)
        total = attendances.count()
        present = attendances.filter(status='present').count()
        percent = int((present / total * 100)) if total > 0 else 0
        
        student_stats.append({
            'student': enrollment,
            'total': total,
            'present': present,
            'absent': total - present,
            'percent': percent
        })
    
    return render(request, 'staff/view_attendance.html', {
        'subject': subject,
        'student_stats': student_stats
    })

def staff_assignments(request):
    """Staff assignments view"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from .models import Assignment, Subject, StudentSubject, StudentAssignment
    from datetime import date
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    staff = request.user.staff_profile
    subjects = staff.subjects.all()
    assignments = Assignment.objects.filter(subject__in=subjects)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        due_date = request.POST.get('due_date')
        total_marks = request.POST.get('total_marks', 100)
        
        subject = get_object_or_404(Subject, id=subject_id)
        assignment = Assignment.objects.create(
            subject=subject,
            title=title,
            due_date=due_date,
            total_marks=total_marks
        )
        
        # Create student assignments for all enrolled students
        students = StudentSubject.objects.filter(subject=subject)
        for enrollment in students:
            StudentAssignment.objects.get_or_create(
                student=enrollment.student,
                assignment=assignment,
                defaults={'status': 'Pending', 'score': 0}
            )
        
        messages.success(request, 'Assignment created successfully!')
        return redirect('staff_assignments')
    
    return render(request, 'staff/assignments.html', {
        'subjects': subjects,
        'assignments': assignments,
        'today': date.today()
    })

def staff_edit_assignment(request, assignment_id):
    """Edit assignment"""
    from django.shortcuts import render, get_object_or_404, redirect
    from django.contrib import messages
    from .models import Assignment
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if request.method == 'POST':
        assignment.title = request.POST.get('title')
        assignment.due_date = request.POST.get('due_date')
        assignment.total_marks = request.POST.get('total_marks')
        assignment.save()
        messages.success(request, 'Assignment updated successfully!')
        return redirect('staff_assignments')
    
    return render(request, 'staff/edit_assignment.html', {'assignment': assignment})

def staff_delete_assignment(request, assignment_id):
    """Delete assignment"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from .models import Assignment
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    assignment.delete()
    messages.success(request, 'Assignment deleted successfully!')
    return redirect('staff_assignments')

def staff_announcements(request):
    """Staff announcements view"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from .models import Announcement, StudentProfile, StudentAnnouncement
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    staff = request.user.staff_profile
    announcements = Announcement.objects.filter(staff=staff)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        announcement_type = request.POST.get('announcement_type', 'general')
        
        announcement = Announcement.objects.create(
            staff=staff,
            title=title,
            content=content,
            announcement_type=announcement_type
        )
        
        # Link to all students
        all_students = StudentProfile.objects.all()
        for student in all_students:
            StudentAnnouncement.objects.get_or_create(
                student=student,
                announcement=announcement,
                defaults={'is_read': False}
            )
        
        messages.success(request, 'Announcement posted successfully!')
        return redirect('staff_announcements')
    
    return render(request, 'staff/announcements.html', {'announcements': announcements})

def staff_edit_announcement(request, announcement_id):
    """Edit announcement"""
    from django.shortcuts import render, get_object_or_404, redirect
    from django.contrib import messages
    from .models import Announcement
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if request.method == 'POST':
        announcement.title = request.POST.get('title')
        announcement.content = request.POST.get('content')
        announcement.announcement_type = request.POST.get('announcement_type')
        announcement.save()
        messages.success(request, 'Announcement updated successfully!')
        return redirect('staff_announcements')
    
    return render(request, 'staff/edit_announcement.html', {'announcement': announcement})

def staff_delete_announcement(request, announcement_id):
    """Delete announcement"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from .models import Announcement
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    announcement = get_object_or_404(Announcement, id=announcement_id)
    announcement.delete()
    messages.success(request, 'Announcement deleted successfully!')
    return redirect('staff_announcements')

def staff_submissions(request):
    """View student submissions"""
    from django.shortcuts import render, get_object_or_404, redirect
    from .models import AssignmentSubmission, Subject
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    staff = request.user.staff_profile
    subjects = staff.subjects.all()
    submissions = AssignmentSubmission.objects.filter(assignment__subject__in=subjects)
    
    selected_subject = None
    subject_id = request.GET.get('subject_id')
    if subject_id:
        selected_subject = get_object_or_404(Subject, id=subject_id)
        submissions = submissions.filter(assignment__subject=selected_subject)
    
    return render(request, 'staff/submissions.html', {
        'subjects': subjects,
        'submissions': submissions,
        'selected_subject': selected_subject
    })

def grade_submission(request, submission_id):
    """Grade a student submission"""
    from django.shortcuts import render, get_object_or_404, redirect
    from django.contrib import messages
    from .models import AssignmentSubmission, StudentAssignment
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    
    if request.method == 'POST':
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback', '')
        
        submission.grade = grade
        submission.feedback = feedback
        submission.status = 'Graded'
        submission.save()
        
        # Update StudentAssignment
        student_assignment, created = StudentAssignment.objects.get_or_create(
            student=submission.student,
            assignment=submission.assignment,
            defaults={'score': grade, 'status': 'Graded'}
        )
        if not created:
            student_assignment.score = grade
            student_assignment.status = 'Graded'
            student_assignment.save()
        
        messages.success(request, f'Grade submitted for {submission.student.user.username}')
        return redirect('staff_submissions')
    
    return render(request, 'staff/grade_submission.html', {'submission': submission})

def staff_profile(request):
    """Staff profile view"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from .models import UserProfile
    
    if not hasattr(request.user, 'staff_profile'):
        return redirect('dashboard')
    
    staff = request.user.staff_profile
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        position = request.POST.get('position')
        qualification = request.POST.get('qualification')
        
        if first_name:
            request.user.first_name = first_name
        if last_name:
            request.user.last_name = last_name
        request.user.save()
        
        if phone:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.phone = phone
            profile.save()
        
        if position:
            staff.position = position
        if qualification:
            staff.qualification = qualification
        staff.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('staff_profile')
    
    return render(request, 'staff/profile.html', {'staff': staff})




def pay_fee(request, fee_id):
    """Student fee payment view"""
    from django.shortcuts import render, get_object_or_404, redirect
    from django.contrib import messages
    from django.contrib.auth.decorators import login_required
    from .models import StudentFee, PaymentRequest
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not hasattr(request.user, 'student_profile'):
        messages.warning(request, 'Access denied. Student only.')
        return redirect('dashboard')
    
    fee = get_object_or_404(StudentFee, id=fee_id, student=request.user.student_profile)
    
    if fee.status == 'Paid':
        messages.warning(request, 'This fee has already been paid.')
        return redirect('my_fee')
    
    if request.method == 'POST':
        reference_number = request.POST.get('reference_number')
        receipt = request.FILES.get('receipt')
        notes = request.POST.get('notes', '')
        
        if not reference_number or not receipt:
            messages.error(request, 'Please provide reference number and payment receipt.')
            return redirect('pay_fee', fee_id=fee_id)
        
        # Create payment request
        payment_request = PaymentRequest.objects.create(
            student=request.user.student_profile,
            fee=fee,
            reference_number=reference_number,
            receipt=receipt,
            notes=notes,
            amount=fee.amount,
            status='pending'
        )
        
        messages.success(request, f'Payment request submitted successfully! Reference: {reference_number}. Your payment will be verified by admin soon.')
        return redirect('my_fee')
    
    return render(request, 'pay_fee.html', {'fee': fee})


def student_register(request):
    """Student registration view"""
    from django.shortcuts import render
    from django.http import JsonResponse
    from .models import RegistrationRequest
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if email already exists
        if RegistrationRequest.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'This email is already registered. Please use a different email or contact administration.'})
        
        try:
            # Create registration request
            registration = RegistrationRequest.objects.create(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=email,
                phone=request.POST.get('phone', ''),
                date_of_birth=request.POST.get('date_of_birth') or None,
                course=request.POST.get('course'),
                year=request.POST.get('year'),
                previous_institution=request.POST.get('previous_institution', ''),
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                status='pending'
            )
            
            return JsonResponse({'status': 'success', 'message': 'Registration submitted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return render(request, 'registration_form.html')


def landing_page(request):
    """Landing page with real statistics from database"""
    from django.shortcuts import render
    from .models import StudentProfile, StaffProfile, Subject, Announcement
    
    # Get real statistics from database
    total_students = StudentProfile.objects.count()
    total_staff = StaffProfile.objects.count()
    total_courses = Subject.objects.count()
    
    # Calculate satisfaction rate (based on active students vs enrolled subjects)
    # For now, use 98% as default, but you can calculate based on attendance or grades
    satisfaction_rate = 98
    
    # Get latest announcements for landing page
    latest_announcements = Announcement.objects.all().order_by('-created_date')[:6]
    
    context = {
        'total_students': total_students,
        'total_staff': total_staff,
        'total_courses': total_courses,
        'satisfaction_rate': satisfaction_rate,
        'announcements': latest_announcements,
    }
    return render(request, 'landing.html', context)


def about_us(request):
    """About Us page"""
    from django.shortcuts import render
    return render(request, 'about.html')


def logout_view(request):
    """Logout user and redirect to login page"""
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    from django.contrib import messages
    
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login')
