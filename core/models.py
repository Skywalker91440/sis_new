from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
import random
import string

class UserProfile(models.Model):
    USER_TYPES = (
        ('admin', 'Administrator'),
        ('staff', 'Staff/Teacher'),
        ('student', 'Student'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='student')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, blank=True)
    full_name = models.CharField(max_length=200, default='')
    department = models.CharField(max_length=100, default='Computer Science')
    year = models.CharField(max_length=20, default='1st Year')
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            existing_ids = StudentProfile.objects.filter(student_id__startswith='SIS').values_list('student_id', flat=True)
            max_num = 0
            for sid in existing_ids:
                try:
                    num = int(sid[7:])
                    if num > max_num:
                        max_num = num
                except:
                    pass
            new_num = max_num + 1
            year = date.today().year
            self.student_id = f"SIS{year}{new_num:05d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student_id} - {self.full_name}"

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    staff_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.CharField(max_length=100, default='Academic')
    position = models.CharField(max_length=100, default='Teacher')
    qualification = models.CharField(max_length=200, blank=True)
    joining_date = models.DateField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.staff_id:
            existing_ids = StaffProfile.objects.filter(staff_id__startswith='STF').values_list('staff_id', flat=True)
            max_num = 0
            for sid in existing_ids:
                try:
                    num = int(sid[7:])
                    if num > max_num:
                        max_num = num
                except:
                    pass
            new_num = max_num + 1
            year = date.today().year
            self.staff_id = f"STF{year}{new_num:05d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.staff_id} - {self.user.get_full_name()}"

class Subject(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    instructor = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')
    schedule = models.CharField(max_length=100, blank=True)
    room = models.CharField(max_length=50, blank=True)
    credits = models.IntegerField(default=3)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class StudentSubject(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='students')
    grade = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='ENROLLED')
    
    class Meta:
        unique_together = ['student', 'subject']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} - Grade: {self.grade}%"

class Assignment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    total_marks = models.IntegerField(default=100)
    
    def __str__(self):
        return self.title

class StudentAssignment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='student_assignments')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='student_assignments')
    score = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='Pending')
    submitted_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'assignment']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.assignment.title} - {self.score}%"

class AssignmentSubmission(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions_received')
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    image = models.ImageField(upload_to='assignment_images/', blank=True, null=True)
    submission_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(default=0, null=True, blank=True)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='Submitted')
    
    class Meta:
        unique_together = ['student', 'assignment']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.assignment.title} - {self.submitted_at}"

class Announcement(models.Model):
    ANNOUNCEMENT_TYPES = (
        ('exam', 'Exam'),
        ('assignment', 'Assignment'),
        ('class', 'Class'),
        ('general', 'General'),
    )
    
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, default='general')
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class StudentAnnouncement(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='announcements_seen')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='seen_by')
    is_read = models.BooleanField(default=False)
    seen_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'announcement']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.announcement.title}"

class Event(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.title

class StudentFee(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='fees')
    fee_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, default='Pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.student_id} - {self.fee_type}"

class StudentAttendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, default='absent')
    
    class Meta:
        unique_together = ['student', 'subject', 'date']
    
    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} - {self.date}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class PaymentRequest(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='payment_requests')
    fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payment_requests')
    reference_number = models.CharField(max_length=100)
    receipt = models.FileField(upload_to='payment_receipts/')
    notes = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    admin_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.student.user.username} - {self.fee.fee_type} - {self.reference_number}"
    
    class Meta:
        ordering = ['-submitted_at']

class RegistrationRequest(models.Model):
    COURSE_CHOICES = (
        ('Computer Science', 'Computer Science'),
        ('Information Technology', 'Information Technology'),
        ('Engineering', 'Engineering'),
        ('Business', 'Business'),
        ('Mathematics', 'Mathematics'),
        ('Science', 'Science'),
    )
    
    YEAR_CHOICES = (
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Academic Information
    course = models.CharField(max_length=100, choices=COURSE_CHOICES)
    year = models.CharField(max_length=20, choices=YEAR_CHOICES)
    previous_institution = models.CharField(max_length=200, blank=True)
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Generated credentials (after approval)
    student_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    generated_password = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email} - {self.status}"
    
    class Meta:
        ordering = ['-submitted_at']
