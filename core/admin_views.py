from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from .models import StudentProfile, StaffProfile, Subject, StudentSubject, Assignment, StudentAssignment, Event, StudentFee, StudentAttendance, Announcement, StudentAnnouncement
import random
import string

def is_admin(user):
    return user.is_authenticated and user.is_staff

def generate_random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# ==================== DASHBOARD ====================
@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_dashboard(request):
    total_students = User.objects.filter(profile__user_type='student').count()
    total_staff = User.objects.filter(profile__user_type='staff').count()
    total_subjects = Subject.objects.count()
    total_payments = StudentFee.objects.filter(status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_payments = StudentFee.objects.filter(status='Pending').aggregate(Sum('amount'))['amount__sum'] or 0
    
    recent_students = StudentProfile.objects.all().order_by('-id')[:5]
    recent_payments = StudentFee.objects.all().order_by('-id')[:5]
    
    context = {
        'total_students': total_students,
        'total_staff': total_staff,
        'total_subjects': total_subjects,
        'total_payments': total_payments,
        'pending_payments': pending_payments,
        'recent_students': recent_students,
        'recent_payments': recent_payments,
    }
    return render(request, 'admin_panel/dashboard.html', context)

# ==================== STUDENT MANAGEMENT ====================
@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_students(request):
    student_profiles = StudentProfile.objects.all().select_related('user')
    
    student_list = []
    for profile in student_profiles:
        student_list.append({
            'id': profile.user.id,
            'student_id': profile.student_id,
            'username': profile.user.username,
            'full_name': profile.full_name,
            'email': profile.user.email,
            'department': profile.department,
            'year': profile.year,
            'phone': profile.user.profile.phone if hasattr(profile.user, 'profile') else '-',
        })
    
    if request.method == 'POST':
        action = request.POST.get('action')
        student_id = request.POST.get('student_id')
        student = get_object_or_404(User, id=student_id)
        
        if action == 'reset_password':
            new_password = request.POST.get('new_password') or generate_random_password()
            student.set_password(new_password)
            student.save()
            messages.success(request, f'Password for {student.username} reset to: {new_password}')
        elif action == 'delete':
            student.delete()
            messages.success(request, f'Student {student.username} deleted successfully!')
        
        return redirect('admin_students')
    
    context = {'students': student_list}
    return render(request, 'admin_panel/students.html', context)

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_add_student(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        department = request.POST.get('department', 'Computer Science')
        year = request.POST.get('year', '1st Year')
        password = request.POST.get('password', 'student123')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists!')
            return redirect('admin_add_student')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        user.profile.user_type = 'student'
        user.profile.phone = phone
        user.profile.save()
        
        full_name = f"{first_name} {last_name}".strip()
        if not full_name:
            full_name = username
        
        student = StudentProfile.objects.create(
            user=user,
            full_name=full_name,
            department=department,
            year=year
        )
        
        # Enroll student in ALL subjects
        all_subjects = Subject.objects.all()
        for subject in all_subjects:
            StudentSubject.objects.get_or_create(
                student=student,
                subject=subject,
                defaults={'grade': 0, 'status': 'ENROLLED'}
            )
        
        # Link all existing announcements
        all_announcements = Announcement.objects.all()
        for announcement in all_announcements:
            StudentAnnouncement.objects.get_or_create(
                student=student,
                announcement=announcement,
                defaults={'is_read': False}
            )
        
        # Link all existing assignments
        for subject in all_subjects:
            assignments = Assignment.objects.filter(subject=subject)
            for assignment in assignments:
                StudentAssignment.objects.get_or_create(
                    student=student,
                    assignment=assignment,
                    defaults={'status': 'Pending', 'score': 0}
                )
        
        messages.success(request, f'Student {username} added successfully! Student ID: {student.student_id}')
        return redirect('admin_students')
    
    context = {}
    return render(request, 'admin_panel/add_student.html', context)

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_student_detail(request, student_id):
    student = get_object_or_404(User, id=student_id)
    profile = student.student_profile
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if phone:
            student.profile.phone = phone
            student.profile.save()
        
        department = request.POST.get('department')
        year = request.POST.get('year')
        if department:
            profile.department = department
        if year:
            profile.year = year
        profile.save()
        
        messages.success(request, 'Student information updated successfully!')
        return redirect('admin_student_detail', student_id=student_id)
    
    enrollments = StudentSubject.objects.filter(student=profile)
    fees = StudentFee.objects.filter(student=profile)
    
    context = {
        'student': student,
        'profile': profile,
        'enrollments': enrollments,
        'fees': fees,
    }
    return render(request, 'admin_panel/student_detail.html', context)

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_add_subject_to_student(request, student_id):
    student = get_object_or_404(User, id=student_id)
    student_profile = student.student_profile
    subjects = Subject.objects.all()
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        grade = request.POST.get('grade', 0)
        subject = get_object_or_404(Subject, id=subject_id)
        
        StudentSubject.objects.get_or_create(
            student=student_profile,
            subject=subject,
            defaults={'grade': grade, 'status': 'ENROLLED'}
        )
        
        # Also create assignments for this subject
        assignments = Assignment.objects.filter(subject=subject)
        for assignment in assignments:
            StudentAssignment.objects.get_or_create(
                student=student_profile,
                assignment=assignment,
                defaults={'status': 'Pending', 'score': 0}
            )
        
        messages.success(request, f'Subject {subject.code} added to {student.username}')
        return redirect('admin_student_detail', student_id=student_id)
    
    context = {'student': student, 'subjects': subjects}
    return render(request, 'admin_panel/add_subject_to_student.html', context)

# ==================== STAFF MANAGEMENT ====================
@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_staff(request):
    staff_profiles = StaffProfile.objects.all().select_related('user')
    
    staff_list = []
    for profile in staff_profiles:
        staff_list.append({
            'id': profile.user.id,
            'staff_id': profile.staff_id,
            'username': profile.user.username,
            'full_name': profile.user.get_full_name() or profile.user.username,
            'email': profile.user.email,
            'department': profile.department,
            'position': profile.position,
            'phone': profile.user.profile.phone if hasattr(profile.user, 'profile') else '-',
        })
    
    if request.method == 'POST':
        action = request.POST.get('action')
        staff_id = request.POST.get('staff_id')
        staff_user = get_object_or_404(User, id=staff_id)
        
        if action == 'reset_password':
            new_password = request.POST.get('new_password') or generate_random_password()
            staff_user.set_password(new_password)
            staff_user.save()
            messages.success(request, f'Password for {staff_user.username} reset to: {new_password}')
        elif action == 'delete':
            staff_user.delete()
            messages.success(request, f'Staff {staff_user.username} deleted successfully!')
        
        return redirect('admin_staff')
    
    context = {'staff_users': staff_list}
    return render(request, 'admin_panel/staff.html', context)

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_add_staff(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        department = request.POST.get('department', 'Academic')
        position = request.POST.get('position', 'Teacher')
        password = request.POST.get('password', 'staff123')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists!')
            return redirect('admin_add_staff')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        user.profile.user_type = 'staff'
        user.profile.phone = phone
        user.profile.save()
        
        staff = StaffProfile.objects.create(
            user=user,
            department=department,
            position=position
        )
        
        messages.success(request, f'Staff {username} added successfully! Staff ID: {staff.staff_id}')
        return redirect('admin_staff')
    
    context = {}
    return render(request, 'admin_panel/add_staff.html', context)

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_staff_detail(request, staff_id):
    staff_user = get_object_or_404(User, id=staff_id)
    staff_profile = staff_user.staff_profile
    
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        position = request.POST.get('position')
        
        if username and username != staff_user.username:
            if not User.objects.filter(username=username).exclude(id=staff_user.id).exists():
                staff_user.username = username
            else:
                messages.error(request, f'Username "{username}" already exists!')
        
        if first_name:
            staff_user.first_name = first_name
        if last_name:
            staff_user.last_name = last_name
        if email:
            staff_user.email = email
        staff_user.save()
        
        if phone:
            staff_user.profile.phone = phone
            staff_user.profile.save()
        
        if department:
            staff_profile.department = department
        if position:
            staff_profile.position = position
        staff_profile.save()
        
        messages.success(request, 'Staff information updated successfully!')
        return redirect('admin_staff_detail', staff_id=staff_id)
    
    context = {
        'staff_user': staff_user,
        'staff_profile': staff_profile,
    }
    return render(request, 'admin_panel/staff_detail.html', context)

# ==================== SUBJECT MANAGEMENT ====================
@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_subjects(request):
    subjects = Subject.objects.all()
    staff_members = StaffProfile.objects.all()
    
    if request.method == 'POST':
        code = request.POST.get('code')
        name = request.POST.get('name')
        instructor_id = request.POST.get('instructor')
        schedule = request.POST.get('schedule', '')
        room = request.POST.get('room', '')
        credits = request.POST.get('credits', 3)
        
        instructor = None
        if instructor_id and instructor_id.isdigit():
            try:
                instructor = StaffProfile.objects.get(id=int(instructor_id))
            except StaffProfile.DoesNotExist:
                pass
        
        Subject.objects.create(
            code=code,
            name=name,
            instructor=instructor,
            schedule=schedule,
            room=room,
            credits=credits
        )
        messages.success(request, f'Subject {code} added successfully!')
        return redirect('admin_subjects')
    
    context = {
        'subjects': subjects,
        'staff_members': staff_members,
    }
    return render(request, 'admin_panel/subjects.html', context)

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject_name = subject.code
    subject.delete()
    messages.success(request, f'Subject {subject_name} deleted successfully!')
    return redirect('admin_subjects')

# ==================== ASSIGNMENT MANAGEMENT ====================
@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_assignments(request):
    assignments = Assignment.objects.all()
    subjects = Subject.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        subject_id = request.POST.get('subject')
        due_date = request.POST.get('due_date')
        total_marks = request.POST.get('total_marks')
        
        if not total_marks:
            total_marks = 100
        
        subject = get_object_or_404(Subject, id=subject_id)
        Assignment.objects.create(
            subject=subject,
            title=title,
            due_date=due_date,
            total_marks=total_marks
        )
        messages.success(request, f'Assignment "{title}" created successfully!')
        return redirect('admin_assignments')
    
    context = {
        'assignments': assignments,
        'subjects': subjects,
    }
    return render(request, 'admin_panel/assignments.html', context)

# ==================== EVENT MANAGEMENT ====================
@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_events(request):
    events = Event.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        date = request.POST.get('date')
        location = request.POST.get('location', '')
        description = request.POST.get('description', '')
        
        Event.objects.create(
            title=title,
            date=date,
            location=location,
            description=description
        )
        messages.success(request, f'Event {title} added successfully!')
        return redirect('admin_events')
    
    context = {'events': events}
    return render(request, 'admin_panel/events.html', context)

# ==================== FEE MANAGEMENT ====================
@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_fees(request):
    fees = StudentFee.objects.all()
    students = StudentProfile.objects.all()
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        fee_type = request.POST.get('fee_type')
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')
        
        student = get_object_or_404(StudentProfile, id=student_id)
        StudentFee.objects.create(
            student=student,
            fee_type=fee_type,
            amount=amount,
            due_date=due_date,
            status='Pending'
        )
        messages.success(request, f'Fee added for {student.user.username} successfully!')
        return redirect('admin_fees')
    
    context = {'fees': fees, 'students': students}
    return render(request, 'admin_panel/fees.html', context)

# ==================== GRADE MANAGEMENT ====================
@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_add_grade(request, enrollment_id):
    enrollment = get_object_or_404(StudentSubject, id=enrollment_id)
    
    if request.method == 'POST':
        grade = request.POST.get('grade')
        enrollment.grade = grade
        enrollment.save()
        messages.success(request, f'Grade {grade}% added for {enrollment.subject.code}')
        return redirect('admin_student_detail', student_id=enrollment.student.user.id)
    
    context = {'enrollment': enrollment}
    return render(request, 'admin_panel/add_grade.html', context)

# ==================== PROFILE PICTURE ====================
@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_upload_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        profile = request.user.profile
        profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        messages.success(request, 'Profile picture updated successfully!')
    return redirect('admin_dashboard')

# ==================== PAYMENT VERIFICATION ====================

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_payment_requests(request):
    """Admin view for payment requests"""
    from .models import PaymentRequest
    
    payment_requests = PaymentRequest.objects.all()
    
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        action = request.POST.get('action')
        
        payment = get_object_or_404(PaymentRequest, id=payment_id)
        
        if action == 'verify':
            payment.status = 'verified'
            payment.verified_at = timezone.now()
            payment.verified_by = request.user
            payment.save()
            
            # Update the fee status
            fee = payment.fee
            fee.status = 'Paid'
            fee.payment_date = timezone.now()
            fee.save()
            
            messages.success(request, f'Payment {payment.reference_number} verified successfully!')
            
        elif action == 'reject':
            payment.status = 'rejected'
            payment.admin_notes = request.POST.get('admin_notes', '')
            payment.save()
            messages.warning(request, f'Payment {payment.reference_number} rejected.')
        
        return redirect('admin_payment_requests')
    
    context = {
        'payment_requests': payment_requests,
        'pending_count': payment_requests.filter(status='pending').count(),
        'verified_count': payment_requests.filter(status='verified').count(),
        'rejected_count': payment_requests.filter(status='rejected').count(),
    }
    return render(request, 'admin_panel/payment_requests.html', context)

@login_required
@user_passes_test(is_admin, login_url='admin_login')

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_profile(request):
    """Admin profile view with picture upload"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from .models import UserProfile
    
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Check if it's a picture upload
        if 'profile_picture' in request.FILES:
            profile_pic = request.FILES['profile_picture']
            profile.profile_picture = profile_pic
            profile.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('admin_profile')
        
        # Regular profile update
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        if first_name:
            request.user.first_name = first_name
        if last_name:
            request.user.last_name = last_name
        if email:
            request.user.email = email
        request.user.save()
        
        if phone:
            profile.phone = phone
            profile.save()
        
        messages.success(request, 'Profile information updated successfully!')
        return redirect('admin_profile')
    
    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'admin_panel/profile.html', context)


@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_change_password(request):
    """Admin change password view"""
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.forms import PasswordChangeForm
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated! Please login again.')
            from django.contrib.auth import logout
            logout(request)
            return redirect('admin_login')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'admin_panel/change_password.html', {'form': form})

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_registration_requests(request):
    """Admin view for registration requests"""
    from .models import RegistrationRequest
    
    requests = RegistrationRequest.objects.all()
    context = {
        'requests': requests,
        'pending_count': requests.filter(status='pending').count(),
        'approved_count': requests.filter(status='approved').count(),
        'rejected_count': requests.filter(status='rejected').count(),
    }
    return render(request, 'admin_panel/registration_requests.html', context)

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_process_registration(request, request_id):
    """Process registration request (accept/decline)"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from django.contrib.auth.models import User
    from django.utils import timezone
    from django.core.mail import send_mail
    from django.conf import settings
    from .models import RegistrationRequest, StudentProfile, UserProfile
    import random
    import string
    
    reg_request = get_object_or_404(RegistrationRequest, id=request_id)
    action = request.POST.get('action')
    
    if action == 'accept':
        try:
            # Generate student ID
            year = timezone.now().year
            last_student = StudentProfile.objects.filter(student_id__startswith=f'SIS{year}').order_by('-student_id').first()
            if last_student:
                last_num = int(last_student.student_id[7:])
                new_num = last_num + 1
            else:
                new_num = 1
            student_id = f"SIS{year}{new_num:05d}"
            
            # Generate random password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Create user account
            username = reg_request.email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=reg_request.email,
                password=password,
                first_name=reg_request.first_name,
                last_name=reg_request.last_name
            )
            
            # Create user profile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.user_type = 'student'
            profile.phone = reg_request.phone
            profile.address = reg_request.address
            profile.save()
            
            # Create student profile
            student = StudentProfile.objects.create(
                user=user,
                student_id=student_id,
                full_name=f"{reg_request.first_name} {reg_request.last_name}",
                department=reg_request.course,
                year=reg_request.year
            )
            
            # Update registration request
            reg_request.status = 'approved'
            reg_request.processed_at = timezone.now()
            reg_request.processed_by = request.user
            reg_request.student_id = student_id
            reg_request.generated_password = password
            reg_request.save()
            
            # Send email to student
            try:
                send_mail(
                    subject='Welcome to SIS Tanzania - Registration Approved!',
                    message=f"""
Dear {reg_request.first_name} {reg_request.last_name},

Congratulations! Your registration has been approved.

Here are your login credentials:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 Student ID: {student_id}
🔑 Password: {password}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please login using the link below:
🔗 http://127.0.0.1:8002/login/

For security reasons, we recommend changing your password after your first login.

Welcome to SIS Tanzania!

Best regards,
SIS Tanzania Administration
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[reg_request.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email error: {e}")
            
            messages.success(request, f'Registration for {reg_request.first_name} {reg_request.last_name} approved! Credentials sent to {reg_request.email}')
            
        except Exception as e:
            messages.error(request, f'Error processing registration: {str(e)}')
    
    elif action == 'decline':
        reg_request.status = 'rejected'
        reg_request.admin_notes = request.POST.get('admin_notes', '')
        reg_request.processed_at = timezone.now()
        reg_request.processed_by = request.user
        reg_request.save()
        
        # Send rejection email
        try:
            send_mail(
                subject='Registration Update - SIS Tanzania',
                message=f"""
Dear {reg_request.first_name} {reg_request.last_name},

We regret to inform you that your registration request has been declined.

Reason: {reg_request.admin_notes or 'Not specified'}

If you have any questions, please contact the administration.

Best regards,
SIS Tanzania Administration
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reg_request.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Email error: {e}")
        
        messages.warning(request, f'Registration for {reg_request.first_name} {reg_request.last_name} declined')
    
    return redirect('admin_registration_requests')
