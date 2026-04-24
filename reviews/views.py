from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .detector import detect_review

@login_required
def submit_review(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    result_data = None
    if request.method == 'POST':
        review_text = request.POST.get('review_text', '').strip()
        if not review_text:
            messages.error(request, 'Please enter a review to analyze.')
        elif len(review_text) < 20:
            messages.error(request, 'Review must be at least 20 characters long.')
        else:
            label, confidence, reasons = detect_review(review_text)
            review = Review.objects.create(
                user=request.user,
                product_name='Review Analysis',
                category='other',
                review_text=review_text,
                result=label,
                confidence=confidence,
                detection_reasons=', '.join(reasons),
            )
            result_data = {
                'label': label,
                'confidence': confidence,
                'reasons': reasons,
                'review_id': review.id,
            }
    return render(request, 'reviews/submit.html', {
        'result_data': result_data,
    })

@login_required
def my_reviews(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    filter_type = request.GET.get('filter', 'all')
    reviews = Review.objects.filter(user=request.user)
    if filter_type == 'CG':
        reviews = reviews.filter(result='CG')
    elif filter_type == 'OR':
        reviews = reviews.filter(result='OR')
    return render(request, 'reviews/my_reviews.html', {
        'reviews': reviews,
        'filter_type': filter_type,
        'total': Review.objects.filter(user=request.user).count(),
        'cg_count': Review.objects.filter(user=request.user, result='CG').count(),
        'or_count': Review.objects.filter(user=request.user, result='OR').count(),
    })

@login_required
def delete_review(request, review_id):
    if request.method != 'POST':
        messages.error(request, 'Invalid request.')
        return redirect('my_reviews')
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    messages.success(request, 'Review deleted successfully.')
    return redirect('my_reviews')
