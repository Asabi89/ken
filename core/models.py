from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    TASK_TYPES = (
        ('watch', 'Watch Video'),
        ('like', 'Like Video'),
        ('subscribe', 'Subscribe Channel'),
        ('question', 'Answer Question'),
        ('game', 'Play Game'),
    )
    
    CATEGORY_CHOICES = (
        ('video', 'Video'),
        ('opinion', 'Share Opinion'),
        ('game', 'Game'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    )
    
    title = models.CharField(max_length=255)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='video')
    video_url = models.URLField()
    channel_url = models.URLField(blank=True, null=True)
    points = models.IntegerField()
    cfa_value = models.DecimalField(max_digits=10, decimal_places=2)
    duration_seconds = models.IntegerField(default=0)
    expires_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    max_completions = models.IntegerField(default=100)
    current_completions = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.task_type})"
    
    def is_available(self):
        return self.status == 'active' and self.current_completions < self.max_completions
    
    def minutes_to_complete(self):
        if self.duration_seconds:
            return round(self.duration_seconds / 60, 1)
        return 1
    
    def get_embed_url(self):
        url = self.video_url
        if 'youtube.com/watch?v=' in url:
            video_id = url.split('watch?v=')[1].split('&')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        elif 'youtube.com/shorts/' in url:
            video_id = url.split('shorts/')[1].split('?')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0]
            return f'https://www.youtube.com/embed/{video_id}'
        return url


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    total_points = models.IntegerField(default=0)
    total_earned_cfa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_balance_cfa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    mobile_money_provider = models.CharField(max_length=50, blank=True, null=True)
    withdrawal_pin = models.CharField(max_length=6, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    is_withdrawal_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.total_points} points"


class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and timezone.now() < self.expires_at


class TaskCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_completions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(default=timezone.now)
    points_earned = models.IntegerField()
    cfa_earned = models.DecimalField(max_digits=10, decimal_places=2)
    proof_screenshot = models.ImageField(upload_to='proofs/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_completions')
    
    class Meta:
        unique_together = ('user', 'task')
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title}"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('earning', 'Task Earning'),
        ('withdrawal', 'Withdrawal'),
        ('bonus', 'Bonus'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount_cfa = models.DecimalField(max_digits=10, decimal_places=2)
    points = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    mobile_money_provider = models.CharField(max_length=50, blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount_cfa} CFA"
