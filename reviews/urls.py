from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_review, name='submit_review'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
]
