from django.contrib import admin
from .models import Task, UserProfile, TaskCompletion, Transaction, EmailVerification


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'available_balance_cfa', 'phone_number', 'is_email_verified', 'is_withdrawal_verified']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['is_email_verified', 'is_withdrawal_verified', 'created_at']


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp_code', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'otp_code']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_type', 'points', 'cfa_value', 'status', 'current_completions', 'max_completions']
    list_filter = ['task_type', 'status', 'created_at']
    search_fields = ['title', 'video_url']


@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'points_earned', 'cfa_earned', 'is_verified', 'completed_at']
    list_filter = ['is_verified', 'completed_at']
    search_fields = ['user__username', 'task__title']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount_cfa', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['user__username', 'reference']
    actions = ['approve_transactions', 'reject_transactions']
    
    def approve_transactions(self, request, queryset):
        queryset.update(status='approved', processed_by=request.user)
    approve_transactions.short_description = "Approve selected transactions"
    
    def reject_transactions(self, request, queryset):
        queryset.update(status='rejected', processed_by=request.user)
    reject_transactions.short_description = "Reject selected transactions"
