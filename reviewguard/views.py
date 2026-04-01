from django.shortcuts import render
from reviews.models import Review
from django.contrib.auth.models import User

def home(request):
    total_reviews = Review.objects.count()
    total_users = User.objects.filter(is_staff=False).count()
    cg_count = Review.objects.filter(result='CG').count()
    or_count = Review.objects.filter(result='OR').count()
    accuracy = 94.7
    context = {
        'total_reviews': total_reviews,
        'total_users': total_users,
        'cg_count': cg_count,
        'or_count': or_count,
        'accuracy': accuracy,
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')

def how_it_works(request):
    return render(request, 'how_it_works.html')
