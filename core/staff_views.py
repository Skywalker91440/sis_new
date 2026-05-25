from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import StaffProfile, Subject, StudentSubject, Assignment, StudentAssignment, Announcement, StudentAnnouncement, StudentAttendance, AssignmentSubmission
from datetime import date

@login_required
def staff_dashboard(request):
    """Staff dashboard view"""
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, 'Access denied. Staff only.')
        return redirect('home')
    
    staff = request.user.staff_profile
    subjects = staff.subjects.all()
    
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

@login_required
def staff_my_courses(request):
    """Staff courses view"""
    if not hasattr(request.user, 'staff_profile'):
        return redirect('home')
    
    staff = request.user.staff_profile
    subjects = staff.subjects.all()
    
    return render(request, 'staff/my_courses.html', {'subjects': subjects})

@login_required
def staff_course_students(request, subject_id):
    """View students in a course"""
    subject = get_object_or_404(Subject, id=subject_id)
    students = StudentSubject.objects.filter(subject=subject).select_related('student')
    
    return render(request, 'staff/course_students.html', {
        'subject': subject,
        'students': students
    })

@login_required
def staff_edit_marks(request, subject_id):
    """Edit student marks"""
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

@login_required
def staff_take_attendance(request, subject_id):
    """Take attendance for a course"""
    subject = get_object_or_404(Subject, id=subject_id)
    students = StudentSubject.objects.filter(subject=subject).select_related('student')
    
    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date', date.today())
        
        for student in students:
            status = request.POST.get(f'attendance_{student.id}')
            if status:
                StudentAttendance.objects.update_or_create(
                    student=student.student,
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

@login_required
def staff_view_attendance(request, subject_id):
    """View attendance records"""
    subject = get_object_or_404(Subject, id=subject_id)
    students = StudentSubject.objects.filter(subject=subject).select_related('student')
    
    # Calculate attendance stats
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

@login_required
def staff_assignments(request):
    """Manage assignments"""
    if not hasattr(request.user, 'staff_profile'):
        return redirect('home')
    
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

@login_required
def staff_edit_assignment(request, assignment_id):
    """Edit assignment"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if request.method == 'POST':
        assignment.title = request.POST.get('title')
        assignment.due_date = request.POST.get('due_date')
        assignment.total_marks = request.POST.get('total_marks')
        assignment.save()
        messages.success(request, 'Assignment updated successfully!')
        return redirect('staff_assignments')
    
    return render(request, 'staff/edit_assignment.html', {'assignment': assignment})

@login_required
def staff_delete_assignment(request, assignment_id):
    """Delete assignment"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    assignment.delete()
    messages.success(request, 'Assignment deleted successfully!')
    return redirect('staff_assignments')

@login_required
def staff_announcements(request):
    """Manage announcements"""
    if not hasattr(request.user, 'staff_profile'):
        return redirect('home')
    
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
        from .models import StudentProfile
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

@login_required
def staff_edit_announcement(request, announcement_id):
    """Edit announcement"""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    
    if request.method == 'POST':
        announcement.title = request.POST.get('title')
        announcement.content = request.POST.get('content')
        announcement.announcement_type = request.POST.get('announcement_type')
        announcement.save()
        messages.success(request, 'Announcement updated successfully!')
        return redirect('staff_announcements')
    
    return render(request, 'staff/edit_announcement.html', {'announcement': announcement})

@login_required
def staff_delete_announcement(request, announcement_id):
    """Delete announcement"""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    announcement.delete()
    messages.success(request, 'Announcement deleted successfully!')
    return redirect('staff_announcements')

@login_required
def staff_submissions(request):
    """View student submissions"""
    if not hasattr(request.user, 'staff_profile'):
        return redirect('home')
    
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

@login_required
def grade_submission(request, submission_id):
    """Grade a student submission"""
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    
    if request.method == 'POST':
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback', '')
        
        submission.grade = grade
        submission.feedback = feedback
        submission.status = 'Graded'
        submission.save()
        
        # Also update StudentAssignment
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

@login_required
def staff_profile(request):
    """Staff profile view"""
    if not hasattr(request.user, 'staff_profile'):
        return redirect('home')
    
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
            request.user.profile.phone = phone
            request.user.profile.save()
        
        if position:
            staff.position = position
        if qualification:
            staff.qualification = qualification
        staff.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('staff_profile')
    
    return render(request, 'staff/profile.html', {'staff': staff})
