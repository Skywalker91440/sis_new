from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import TeacherProfile, Subject, Enrollment, Assignment, Submission, Attendance
from datetime import date

def is_teacher(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.user_type == 'teacher'

@login_required
@user_passes_test(is_teacher, login_url='login')
def teacher_dashboard(request):
    teacher_profile = request.user.profile.teacher_profile
    subjects = Subject.objects.filter(teacher=teacher_profile)
    
    total_students = Enrollment.objects.filter(subject__in=subjects).values('student').distinct().count()
    pending_assignments = Submission.objects.filter(assignment__subject__in=subjects, status='PENDING').count()
    
    context = {
        'my_subjects': subjects,
        'total_students': total_students,
        'pending_assignments': pending_assignments,
    }
    return render(request, 'teacher/dashboard.html', context)

@login_required
@user_passes_test(is_teacher, login_url='login')
def teacher_subject_students(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    enrollments = Enrollment.objects.filter(subject=subject)
    
    if request.method == 'POST':
        for enrollment in enrollments:
            grade = request.POST.get(f'grade_{enrollment.id}')
            if grade:
                enrollment.grade = grade
                enrollment.save()
        messages.success(request, 'Grades updated successfully!')
        return redirect('teacher_subject_students', subject_id=subject_id)
    
    return render(request, 'teacher/subject_students.html', {'subject': subject, 'enrollments': enrollments})

@login_required
@user_passes_test(is_teacher, login_url='login')
def teacher_grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    
    if request.method == 'POST':
        score = request.POST.get('score')
        feedback = request.POST.get('feedback')
        
        submission.score = score
        submission.feedback = feedback
        submission.status = 'GRADED'
        submission.save()
        
        messages.success(request, f'Grade added successfully!')
        return redirect('teacher_dashboard')
    
    return render(request, 'teacher/grade_submission.html', {'submission': submission})

@login_required
@user_passes_test(is_teacher, login_url='login')
def teacher_attendance(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    enrollments = Enrollment.objects.filter(subject=subject)
    today = date.today()
    
    if request.method == 'POST':
        for enrollment in enrollments:
            status = request.POST.get(f'attendance_{enrollment.id}')
            if status:
                Attendance.objects.update_or_create(
                    student=enrollment.student,
                    subject=subject,
                    date=today,
                    defaults={'status': status}
                )
        messages.success(request, 'Attendance recorded successfully!')
        return redirect('teacher_subject_students', subject_id=subject_id)
    
    return render(request, 'teacher/attendance.html', {'subject': subject, 'enrollments': enrollments})
