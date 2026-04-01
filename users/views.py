from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegisterForm, UserLoginForm
from reviews.models import Review

def user_register(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('user_login')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('user_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Only allow registered non-admin users
        try:
            user_obj = User.objects.get(username=username)
            if user_obj.is_staff:
                messages.error(request, 'Admin accounts must use the admin login page.')
                return render(request, 'users/login.html', {})
        except User.DoesNotExist:
            messages.error(request, 'No account found with this username. Please register first.')
            return render(request, 'users/login.html', {})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid password. Please try again.')
    return render(request, 'users/login.html', {})

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def user_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    total = reviews.count()
    cg_count = reviews.filter(result='CG').count()
    or_count = reviews.filter(result='OR').count()
    recent = reviews[:5]
    context = {
        'total': total,
        'cg_count': cg_count,
        'or_count': or_count,
        'recent_reviews': recent,
    }
    return render(request, 'users/dashboard.html', context)
