from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, StudentProfile, StaffProfile, Subject, StudentSubject, Assignment, StudentAssignment, Event, StudentFee, StudentAttendance, Announcement

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')
    list_filter = ('is_staff', 'is_superuser', 'profile__user_type')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_user_type(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_user_type_display()
        return '-'
    get_user_type.short_description = 'User Type'

# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'date_joined']
    list_filter = ['user_type']
    search_fields = ['user__username', 'user__email', 'phone']

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'department', 'year']
    list_filter = ['department', 'year']
    search_fields = ['student_id', 'user__username', 'user__email']
    readonly_fields = ['student_id']

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['staff_id', 'user', 'department', 'position']
    list_filter = ['department', 'position']
    search_fields = ['staff_id', 'user__username', 'user__email']
    readonly_fields = ['staff_id']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'instructor', 'credits']
    list_filter = ['credits']
    search_fields = ['code', 'name']

@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'grade', 'status']
    list_filter = ['status']
    search_fields = ['student__student_id', 'subject__code']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'due_date', 'total_marks']
    list_filter = ['due_date']
    search_fields = ['title']

@admin.register(StudentAssignment)
class StudentAssignmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'score', 'status']
    list_filter = ['status']
    search_fields = ['student__student_id', 'assignment__title']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'staff', 'announcement_type', 'created_date']
    list_filter = ['announcement_type', 'created_date']
    search_fields = ['title', 'content']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location']
    search_fields = ['title']

@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_type', 'amount', 'due_date', 'status']
    list_filter = ['status']
    search_fields = ['student__student_id', 'fee_type']

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status']
    list_filter = ['status', 'date']
    search_fields = ['student__student_id', 'subject__code']
