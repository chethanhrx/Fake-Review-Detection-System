from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = [
    ('electronics', 'Electronics'),
    ('clothing', 'Clothing & Fashion'),
    ('food', 'Food & Beverages'),
    ('beauty', 'Beauty & Personal Care'),
    ('home', 'Home & Kitchen'),
    ('books', 'Books & Education'),
    ('sports', 'Sports & Outdoors'),
    ('travel', 'Travel & Hotels'),
    ('software', 'Software & Apps'),
    ('other', 'Other'),
]

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    review_text = models.TextField()
    result = models.CharField(max_length=5, choices=[('CG', 'Computer Generated'), ('OR', 'Original Review')])
    confidence = models.FloatField(default=0.0)
    detection_reasons = models.TextField(blank=True, default='')
    is_flagged = models.BooleanField(default=False)
    admin_override = models.CharField(max_length=5, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product_name} [{self.result}]"

    @property
    def final_result(self):
        return self.admin_override if self.admin_override else self.result

    @property
    def short_text(self):
        return self.review_text[:120] + '...' if len(self.review_text) > 120 else self.review_text
