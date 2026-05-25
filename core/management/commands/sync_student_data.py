from django.core.management.base import BaseCommand
from core.models import StudentProfile, Announcement, StudentAnnouncement, Assignment, StudentAssignment, StudentSubject, Subject

class Command(BaseCommand):
    help = 'Sync announcements and assignments for all students'
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Syncing student data...")
        
        # Sync announcements
        students = StudentProfile.objects.all()
        announcements = Announcement.objects.all()
        
        for student in students:
            for announcement in announcements:
                obj, created = StudentAnnouncement.objects.get_or_create(
                    student=student,
                    announcement=announcement,
                    defaults={'is_read': False}
                )
                if created:
                    self.stdout.write(f"Created announcement for {student.full_name}")
        
        # Sync assignments
        for student in students:
            subjects = StudentSubject.objects.filter(student=student)
            for enrollment in subjects:
                assignments = Assignment.objects.filter(subject=enrollment.subject)
                for assignment in assignments:
                    obj, created = StudentAssignment.objects.get_or_create(
                        student=student,
                        assignment=assignment,
                        defaults={'status': 'Pending', 'score': 0}
                    )
                    if created:
                        self.stdout.write(f"Created assignment for {student.full_name}")
        
        self.stdout.write(self.style.SUCCESS("Sync completed!"))
