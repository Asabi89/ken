from django.contrib import admin
from django.utils import timezone
from .models import Task, UserProfile, TaskCompletion, Transaction, EmailVerification, InfluencerProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'available_balance_usd', 'phone_number', 'is_email_verified', 'is_withdrawal_verified']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['is_email_verified', 'is_withdrawal_verified', 'created_at']


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp_code', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'otp_code']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_type', 'points', 'usd_value', 'status', 'current_completions', 'max_completions']
    list_filter = ['task_type', 'status', 'created_at']
    search_fields = ['title', 'video_url']


@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'points_earned', 'usd_earned', 'is_verified', 'completed_at']
    list_filter = ['is_verified', 'completed_at']
    search_fields = ['user__username', 'task__title']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount_usd', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['user__username', 'reference']
    actions = ['approve_transactions', 'reject_transactions']
    
    def approve_transactions(self, request, queryset):
        queryset.update(status='approved', processed_by=request.user)
    approve_transactions.short_description = "Approve selected transactions"
    
    def reject_transactions(self, request, queryset):
        queryset.update(status='rejected', processed_by=request.user)
    reject_transactions.short_description = "Reject selected transactions"


@admin.register(InfluencerProfile)
class InfluencerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'status', 'is_verified', 'total_tasks_created', 'budget_limit', 'total_budget_spent', 'created_at']
    list_filter = ['status', 'is_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'company_name', 'phone_number']
    readonly_fields = ['total_tasks_created', 'total_budget_spent', 'created_at', 'updated_at', 'remaining_budget_display']
    actions = ['approve_influencers', 'reject_influencers', 'suspend_influencers']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'company_name', 'phone_number', 'website', 'social_media')
        }),
        ('Profile', {
            'fields': ('bio', 'profile_picture')
        }),
        ('Status', {
            'fields': ('status', 'is_verified', 'rejection_reason')
        }),
        ('Approval', {
            'fields': ('approved_at', 'approved_by')
        }),
        ('Budget Management', {
            'fields': ('budget_limit', 'total_budget_spent', 'remaining_budget_display')
        }),
        ('Statistics', {
            'fields': ('total_tasks_created',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def remaining_budget_display(self, obj):
        remaining = obj.get_remaining_budget()
        if remaining is None:
            return "Unlimited"
        if remaining < 0:
            return f"${remaining:.2f} (Over budget!)"
        return f"${remaining:.2f}"
    remaining_budget_display.short_description = "Remaining Budget"
    
    def approve_influencers(self, request, queryset):
        count = queryset.update(
            status='approved',
            approved_at=timezone.now(),
            approved_by=request.user
        )
        self.message_user(request, f'{count} influencer(s) approved successfully')
    approve_influencers.short_description = "Approve selected influencers"
    
    def reject_influencers(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f'{count} influencer(s) rejected')
    reject_influencers.short_description = "Reject selected influencers"
    
    def suspend_influencers(self, request, queryset):
        count = queryset.update(status='suspended')
        self.message_user(request, f'{count} influencer(s) suspended')
    suspend_influencers.short_description = "Suspend selected influencers"
