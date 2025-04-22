from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def login_view(request):
    """Render the login page."""
    return render(request, 'core/login.html')

@require_http_methods(["GET"])
def register_view(request):
    """Render the registration page."""
    return render(request, 'core/register.html')

@login_required
@require_http_methods(["GET"])
def dashboard_view(request):
    """Render the dashboard page."""
    return render(request, 'core/dashboard.html') 