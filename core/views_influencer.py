from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import random

from .models import (
    InfluencerProfile, Task, TaskCompletion, 
    EmailVerification, User
)
from .forms_influencer import InfluencerSignUpForm, InfluencerTaskForm


def influencer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'influencer_profile'):
            messages.error(request, 'You need an influencer account to access this page.')
            return redirect('influencer_signup')
        
        if request.user.influencer_profile.status != 'approved':
            messages.warning(request, 'Your influencer account is pending approval.')
            return redirect('influencer_dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def influencer_signup_view(request):
    if request.user.is_authenticated and hasattr(request.user, 'influencer_profile'):
        return redirect('influencer_dashboard')
    
    if request.method == 'POST':
        form = InfluencerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            InfluencerProfile.objects.create(
                user=user,
                company_name=form.cleaned_data.get('company_name'),
                phone_number=form.cleaned_data.get('phone_number'),
                website=form.cleaned_data.get('website'),
                social_media=form.cleaned_data.get('social_media'),
                bio=form.cleaned_data.get('bio'),
                status='pending'
            )
            
            otp_code = str(random.randint(100000, 999999))
            EmailVerification.objects.create(
                user=user,
                otp_code=otp_code,
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            
            from .email_templates import get_otp_email_html, get_otp_email_text
            
            try:
                send_mail(
                    'Ken Influencer - Email Verification Code',
                    get_otp_email_text(user.username, otp_code),
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                    html_message=get_otp_email_html(user.username, otp_code)
                )
                messages.success(request, f'OTP sent to {user.email}')
            except Exception as e:
                messages.warning(request, f'Email not sent. Your OTP code is: {otp_code}')
            
            login(request, user)
            return redirect('influencer_verify_email')
    else:
        form = InfluencerSignUpForm()
    
    return render(request, 'influencer/influencer_signup.html', {'form': form})


@login_required
def influencer_verify_email_view(request):
    if not hasattr(request.user, 'influencer_profile'):
        return redirect('influencer_signup')
    
    if request.user.influencer_profile.is_verified:
        return redirect('influencer_dashboard')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        
        otp = EmailVerification.objects.filter(
            user=request.user,
            otp_code=otp_code,
            is_used=False
        ).first()
        
        if otp and otp.is_valid():
            otp.is_used = True
            otp.save()
            
            influencer_profile = request.user.influencer_profile
            influencer_profile.is_verified = True
            influencer_profile.save()
            
            messages.success(request, 'Email verified! Your account is pending admin approval.')
            return redirect('influencer_dashboard')
        else:
            messages.error(request, 'Invalid or expired OTP code!')
    
    return render(request, 'influencer/influencer_verify_email.html')


@login_required
def influencer_dashboard_view(request):
    if not hasattr(request.user, 'influencer_profile'):
        return redirect('influencer_signup')
    
    influencer_profile = request.user.influencer_profile
    
    # If influencer is not approved, show limited dashboard
    if influencer_profile.status != 'approved':
        context = {
            'influencer_profile': influencer_profile,
            'total_tasks': 0,
            'total_completions': 0,
            'pending_proofs': 0,
            'total_budget': 0,
            'recent_tasks': [],
            'recent_completions': [],
        }
        return render(request, 'influencer/influencer_dashboard.html', context)
    
    total_tasks = Task.objects.filter(created_by=request.user).count()
    total_completions = TaskCompletion.objects.filter(task__created_by=request.user).count()
    pending_proofs = TaskCompletion.objects.filter(
        task__created_by=request.user,
        is_verified=False,
        proof_screenshot__isnull=False
    ).count()
    total_budget = Task.objects.filter(created_by=request.user).aggregate(
        total=Sum('usd_value')
    )['total'] or 0
    
    recent_tasks = Task.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    recent_completions = TaskCompletion.objects.filter(
        task__created_by=request.user
    ).order_by('-completed_at')[:10]
    
    context = {
        'influencer_profile': influencer_profile,
        'total_tasks': total_tasks,
        'total_completions': total_completions,
        'pending_proofs': pending_proofs,
        'total_budget': total_budget,
        'recent_tasks': recent_tasks,
        'recent_completions': recent_completions,
    }
    
    return render(request, 'influencer/influencer_dashboard.html', context)


@login_required
@influencer_required
def influencer_task_create_view(request):
    influencer_profile = request.user.influencer_profile
    
    if request.method == 'POST':
        form = InfluencerTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            
            from decimal import Decimal
            
            # Calculate total task cost
            total_cost = Decimal(str(task.usd_value)) * Decimal(str(task.max_completions))
            
            # Check budget limit
            if not influencer_profile.has_budget_available(total_cost):
                remaining = influencer_profile.get_remaining_budget()
                if remaining is not None:
                    messages.error(request, f'Insufficient budget! You have ${remaining:.2f} remaining, but this task costs ${total_cost:.2f}.')
                else:
                    messages.error(request, 'Cannot create task due to budget restrictions.')
                return render(request, 'influencer/influencer_task_create.html', {'form': form, 'influencer_profile': influencer_profile})
            
            task.created_by = request.user
            task.status = 'active'
            task.save()
            
            influencer_profile.total_tasks_created += 1
            influencer_profile.total_budget_spent += total_cost
            influencer_profile.save()
            
            messages.success(request, 'Task created successfully!')
            return redirect('influencer_task_detail', task_id=task.id)
    else:
        form = InfluencerTaskForm()
    
    context = {
        'form': form,
        'influencer_profile': influencer_profile,
    }
    return render(request, 'influencer/influencer_task_create.html', context)


@login_required
@influencer_required
def influencer_task_list_view(request):
    status_filter = request.GET.get('status', 'all')
    
    tasks = Task.objects.filter(created_by=request.user)
    
    if status_filter != 'all':
        tasks = tasks.filter(status=status_filter)
    
    tasks = tasks.order_by('-created_at')
    
    context = {
        'tasks': tasks,
        'current_status': status_filter,
    }
    
    return render(request, 'influencer/influencer_task_list.html', context)


@login_required
@influencer_required
def influencer_task_detail_view(request, task_id):
    task = get_object_or_404(Task, id=task_id, created_by=request.user)
    
    completions = TaskCompletion.objects.filter(task=task).order_by('-completed_at')
    verified_count = completions.filter(is_verified=True).count()
    pending_count = completions.filter(is_verified=False, proof_screenshot__isnull=False).count()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'pause':
            task.status = 'paused'
            task.save()
            messages.success(request, 'Task paused successfully!')
        elif action == 'activate':
            task.status = 'active'
            task.save()
            messages.success(request, 'Task activated successfully!')
        return redirect('influencer_task_detail', task_id=task_id)
    
    context = {
        'task': task,
        'completions': completions,
        'verified_count': verified_count,
        'pending_count': pending_count,
    }
    
    return render(request, 'influencer/influencer_task_detail.html', context)


@login_required
@influencer_required
def influencer_proofs_view(request):
    status_filter = request.GET.get('status', 'pending')
    
    proofs = TaskCompletion.objects.filter(
        task__created_by=request.user,
        proof_screenshot__isnull=False
    )
    
    if status_filter == 'pending':
        proofs = proofs.filter(is_verified=False)
    elif status_filter == 'verified':
        proofs = proofs.filter(is_verified=True)
    
    proofs = proofs.order_by('-completed_at')
    
    context = {
        'proofs': proofs,
        'current_status': status_filter,
    }
    
    return render(request, 'influencer/influencer_proofs.html', context)


@login_required
@influencer_required
def influencer_approve_proof_view(request, proof_id):
    proof = get_object_or_404(
        TaskCompletion, 
        id=proof_id, 
        task__created_by=request.user
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            proof.is_verified = True
            proof.verified_at = timezone.now()
            proof.verified_by = request.user
            proof.save()
            
            user_profile = proof.user.profile
            user_profile.total_points += proof.points_earned
            user_profile.total_earned_usd += proof.usd_earned
            user_profile.available_balance_usd += proof.usd_earned
            user_profile.save()
            
            from .models import Transaction
            Transaction.objects.create(
                user=proof.user,
                transaction_type='earning',
                amount_usd=proof.usd_earned,
                points=proof.points_earned,
                status='completed'
            )
            
            messages.success(request, 'Proof approved successfully!')
        
        elif action == 'reject':
            proof.delete()
            messages.success(request, 'Proof rejected and deleted!')
        
        return redirect('influencer_proofs')
    
    context = {
        'proof': proof,
    }
    
    return render(request, 'influencer/influencer_approve_proof.html', context)
