from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse

def is_admin(user):
    """Check if user is admin (staff member)"""
    return user.is_authenticated and user.is_staff

def admin_login_view(request):
    """Admin-only login page"""
    # If already logged in as admin, redirect to admin dashboard
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            # If student is logged in and tries to access admin login, logout them first
            from django.contrib.auth import logout
            logout(request)
            messages.warning(request, 'Please login with admin credentials')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome Admin {username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'You do not have admin privileges. This area is for administrators only.')
        else:
            messages.error(request, 'Invalid admin credentials')
    
    return render(request, 'admin_login.html')

@login_required
@user_passes_test(is_admin, login_url='admin_login')
def admin_dashboard_secure(request):
    """Secure admin dashboard - only accessible by admin"""
    from .admin_views import admin_dashboard
    return admin_dashboard(request)
