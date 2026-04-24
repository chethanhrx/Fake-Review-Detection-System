from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from reviews.models import Review
from django.conf import settings

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'Admin access required. Please login as admin.')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def admin_register(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        secret_key = request.POST.get('secret_key', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if secret_key != settings.ADMIN_SECRET_KEY:
            messages.error(request, 'Invalid admin secret key. Access denied.')
            return render(request, 'admin_panel/admin_register.html', {})
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'admin_panel/admin_register.html', {})
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'admin_panel/admin_register.html', {})
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'admin_panel/admin_register.html', {})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=True,
        )
        messages.success(request, 'Admin account created! Please login.')
        return redirect('admin_login')
    return render(request, 'admin_panel/admin_register.html', {})

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        try:
            user_obj = User.objects.get(username=username)
            if not user_obj.is_staff:
                messages.error(request, 'This account is not an admin account. Use the user login page.')
                return render(request, 'admin_panel/admin_login.html', {})
        except User.DoesNotExist:
            messages.error(request, 'No admin account found with this username. Please register first.')
            return render(request, 'admin_panel/admin_login.html', {})
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid password. Please try again.')
    return render(request, 'admin_panel/admin_login.html', {})

def admin_logout(request):
    logout(request)
    return redirect('home')

@admin_required
def admin_dashboard(request):
    total_users = User.objects.filter(is_staff=False).count()
    total_admins = User.objects.filter(is_staff=True).count()
    total_reviews = Review.objects.count()
    cg_count = Review.objects.filter(result='CG').count()
    or_count = Review.objects.filter(result='OR').count()

    today = timezone.now().date()
    today_reviews = Review.objects.filter(created_at__date=today).count()
    week_ago = timezone.now() - timedelta(days=7)
    week_reviews = Review.objects.filter(created_at__gte=week_ago).count()

    recent_users = User.objects.filter(is_staff=False).order_by('-date_joined')[:6]
    recent_reviews = Review.objects.select_related('user').order_by('-created_at')[:8]

    # Reviews per day last 7 days for chart
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        day = timezone.now().date() - timedelta(days=i)
        count = Review.objects.filter(created_at__date=day).count()
        chart_labels.append(day.strftime('%b %d'))
        chart_data.append(count)

    # Top users by review count
    top_users = User.objects.filter(is_staff=False).annotate(
        review_count=Count('reviews')
    ).order_by('-review_count')[:5]

    context = {
        'total_users': total_users,
        'total_admins': total_admins,
        'total_reviews': total_reviews,
        'cg_count': cg_count,
        'or_count': or_count,
        'today_reviews': today_reviews,
        'week_reviews': week_reviews,
        'recent_users': recent_users,
        'recent_reviews': recent_reviews,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'top_users': top_users,
        'cg_percent': round((cg_count / total_reviews * 100), 1) if total_reviews else 0,
        'or_percent': round((or_count / total_reviews * 100), 1) if total_reviews else 0,
    }
    return render(request, 'admin_panel/admin_dashboard.html', context)

@admin_required
def admin_reviews(request):
    filter_type = request.GET.get('filter', 'all')
    search = request.GET.get('search', '').strip()

    reviews = Review.objects.select_related('user').all()
    if filter_type == 'CG':
        reviews = reviews.filter(result='CG')
    elif filter_type == 'OR':
        reviews = reviews.filter(result='OR')
    elif filter_type == 'flagged':
        reviews = reviews.filter(is_flagged=True)

    if search:
        reviews = reviews.filter(
            Q(user__username__icontains=search) | Q(product_name__icontains=search)
        )

    total = Review.objects.count()
    cg_count = Review.objects.filter(result='CG').count()
    or_count = Review.objects.filter(result='OR').count()
    flagged_count = Review.objects.filter(is_flagged=True).count()

    context = {
        'reviews': reviews,
        'filter_type': filter_type,
        'search': search,
        'total': total,
        'cg_count': cg_count,
        'or_count': or_count,
        'flagged_count': flagged_count,
    }
    return render(request, 'admin_panel/admin_reviews.html', context)

@admin_required
def toggle_flag(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.is_flagged = not review.is_flagged
    review.save()
    messages.success(request, f'Review {"flagged" if review.is_flagged else "unflagged"} successfully.')
    return redirect('admin_reviews')

@admin_required
def override_result(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        new_result = request.POST.get('new_result')
        if new_result in ['CG', 'OR']:
            review.admin_override = new_result
            review.save()
            messages.success(request, f'Review result overridden to {new_result}.')
    return redirect('admin_reviews')

@admin_required
def admin_delete_review(request, review_id):
    if request.method != 'POST':
        messages.error(request, 'Invalid request.')
        return redirect('admin_reviews')
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect('admin_reviews')

@admin_required
def admin_users(request):
    users = User.objects.filter(is_staff=False).annotate(
        review_count=Count('reviews')
    ).order_by('-date_joined')
    context = {'users': users}
    return render(request, 'admin_panel/admin_users.html', context)
