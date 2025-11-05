from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from .models import Task, UserProfile, TaskCompletion, Transaction
from .forms import SignUpForm, LoginForm, TaskForm, WithdrawalForm


def landing_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'influencer_profile'):
            if not request.user.influencer_profile.is_verified:
                return redirect('influencer_verify_email')
            return redirect('influencer_dashboard')
        return redirect('dashboard')
    return render(request, 'core/landing.html')


def signup_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'influencer_profile'):
            if not request.user.influencer_profile.is_verified:
                return redirect('influencer_verify_email')
            return redirect('influencer_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data.get('email')
            user.save()
            
            phone_number = form.cleaned_data.get('phone_number')
            user_type = form.cleaned_data.get('user_type')
            company_name = form.cleaned_data.get('company_name')
            
            if user_type == 'influencer':
                from .models import InfluencerProfile
                InfluencerProfile.objects.create(
                    user=user,
                    phone_number=phone_number or '',
                    company_name=company_name or '',
                    is_verified=False,
                    status='pending'
                )
                
                import random
                from datetime import timedelta
                from .models import EmailVerification
                
                otp_code = str(random.randint(100000, 999999))
                EmailVerification.objects.create(
                    user=user,
                    otp_code=otp_code,
                    expires_at=timezone.now() + timedelta(minutes=10)
                )
                
                from django.core.mail import send_mail
                from django.conf import settings
                from .email_templates import get_otp_email_html, get_otp_email_text
                
                try:
                    send_mail(
                        'Ken - Email Verification Code',
                        get_otp_email_text(user.username, otp_code),
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                        html_message=get_otp_email_html(user.username, otp_code)
                    )
                except:
                    pass
                
                login(request, user)
                messages.success(request, 'Account created! Please verify your email.')
                return redirect('influencer_verify_email')
            else:
                UserProfile.objects.create(user=user, phone_number=phone_number or '')
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'influencer_profile'):
            if not request.user.influencer_profile.is_verified:
                return redirect('influencer_verify_email')
            return redirect('influencer_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            if hasattr(user, 'influencer_profile'):
                if not user.influencer_profile.is_verified:
                    return redirect('influencer_verify_email')
                return redirect('influencer_dashboard')
            return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')


@login_required
def dashboard_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    available_tasks = Task.objects.filter(status='active').exclude(
        completions__user=request.user
    )[:10]
    
    recent_completions = TaskCompletion.objects.filter(
        user=request.user
    ).order_by('-completed_at')[:5]
    
    context = {
        'profile': profile,
        'available_tasks': available_tasks,
        'recent_completions': recent_completions,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def task_list_view(request):
    from django.core.paginator import Paginator
    
    category = request.GET.get('category', 'all')
    
    available_tasks = Task.objects.filter(status='active').exclude(
        completions__user=request.user
    )
    
    if category != 'all':
        available_tasks = available_tasks.filter(category=category)
    
    paginator = Paginator(available_tasks, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_category': category,
    }
    return render(request, 'core/task_list.html', context)


@login_required
def task_detail_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    already_completed = TaskCompletion.objects.filter(user=request.user, task=task).exists()
    
    context = {
        'task': task,
        'already_completed': already_completed,
    }
    return render(request, 'core/task_detail.html', context)


@login_required
def complete_task_view(request, task_id):
    from .forms import TaskCompletionForm
    
    task = get_object_or_404(Task, id=task_id)
    
    if TaskCompletion.objects.filter(user=request.user, task=task).exists():
        messages.error(request, 'You have already completed this task!')
        return redirect('task_detail', task_id=task_id)
    
    if request.method == 'POST':
        needs_proof = task.task_type in ['like', 'subscribe', 'question']
        
        if needs_proof:
            form = TaskCompletionForm(request.POST, request.FILES)
            if not form.is_valid() or not request.FILES.get('proof_screenshot'):
                messages.error(request, 'Please upload a screenshot as proof!')
                return redirect('task_detail', task_id=task_id)
        
        profile = request.user.profile
        
        completion = TaskCompletion.objects.create(
            user=request.user,
            task=task,
            points_earned=task.points,
            usd_earned=task.usd_value,
            is_verified=False if needs_proof else True,
            proof_screenshot=request.FILES.get('proof_screenshot') if needs_proof else None
        )
        
        if not needs_proof:
            profile.total_points += task.points
            profile.total_earned_usd += task.usd_value
            profile.available_balance_usd += task.usd_value
            profile.save()
            
            Transaction.objects.create(
                user=request.user,
                transaction_type='earning',
                amount_usd=task.usd_value,
                points=task.points,
                status='completed'
            )
        
        task.current_completions += 1
        task.save()
        
        if needs_proof:
            messages.success(request, 'Task submitted! Waiting for admin verification.')
        else:
            messages.success(request, f'Task completed! You earned {task.points} points and ${task.usd_value}!')
        
        return redirect('dashboard')
    
    return redirect('task_detail', task_id=task_id)


@login_required
def withdrawal_view(request):
    from .forms import WithdrawalSetupForm, VerifyOTPForm, WithdrawalForm
    from .models import EmailVerification
    import random
    from datetime import timedelta
    
    profile = request.user.profile
    
    step = request.GET.get('step', 'check')
    
    if step == 'check':
        if not profile.is_withdrawal_verified:
            return redirect('/withdrawal/?step=setup')
        elif not profile.is_email_verified:
            return redirect('/withdrawal/?step=verify')
        else:
            return redirect('/withdrawal/?step=withdraw')
    
    elif step == 'setup':
        if request.method == 'POST':
            form = WithdrawalSetupForm(request.POST, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.withdrawal_pin = form.cleaned_data['pin']
                profile.save()
                
                otp_code = str(random.randint(100000, 999999))
                EmailVerification.objects.create(
                    user=request.user,
                    otp_code=otp_code,
                    expires_at=timezone.now() + timedelta(minutes=10)
                )
                
                from django.core.mail import send_mail
                from django.conf import settings
                from .email_templates import get_otp_email_html, get_otp_email_text
                
                try:
                    send_mail(
                        'Ken - Email Verification Code',
                        get_otp_email_text(request.user.username, otp_code),
                        settings.DEFAULT_FROM_EMAIL,
                        [request.user.email],
                        fail_silently=False,
                        html_message=get_otp_email_html(request.user.username, otp_code)
                    )
                    messages.success(request, f'OTP sent to {request.user.email}')
                except Exception as e:
                    messages.warning(request, f'Email not sent. Your OTP code is: {otp_code}')
                return redirect('/withdrawal/?step=verify')
        else:
            form = WithdrawalSetupForm(instance=profile)
        
        context = {'form': form, 'profile': profile, 'step': 'setup'}
        return render(request, 'core/withdrawal_setup.html', context)
    
    elif step == 'verify':
        if request.method == 'POST':
            form = VerifyOTPForm(request.POST)
            if form.is_valid():
                otp = EmailVerification.objects.filter(
                    user=request.user, 
                    otp_code=form.cleaned_data['otp_code'],
                    is_used=False
                ).first()
                
                if otp and otp.is_valid():
                    otp.is_used = True
                    otp.save()
                    profile.is_email_verified = True
                    profile.is_withdrawal_verified = True
                    profile.save()
                    messages.success(request, 'Email verified successfully!')
                    return redirect('/withdrawal/?step=withdraw')
                else:
                    messages.error(request, 'Invalid or expired OTP code!')
        else:
            form = VerifyOTPForm()
        
        context = {'form': form, 'profile': profile, 'step': 'verify'}
        return render(request, 'core/withdrawal_verify.html', context)
    
    else:
        if request.method == 'POST':
            form = WithdrawalForm(request.POST)
            pin = request.POST.get('pin')
            
            if profile.withdrawal_pin != pin:
                messages.error(request, 'Invalid PIN!')
                return redirect('/withdrawal/?step=withdraw')
            
            if form.is_valid():
                amount = form.cleaned_data['amount_usd']
                
                if amount < 50:
                    messages.error(request, 'Minimum withdrawal is $50!')
                    return redirect('/withdrawal/?step=withdraw')
                
                if amount > profile.available_balance_usd:
                    messages.error(request, 'Insufficient balance!')
                    return redirect('/withdrawal/?step=withdraw')
                
                withdrawal = form.save(commit=False)
                withdrawal.user = request.user
                withdrawal.transaction_type = 'withdrawal'
                withdrawal.status = 'pending'
                withdrawal.save()
                
                profile.available_balance_usd -= amount
                profile.save()
                
                messages.success(request, 'Withdrawal submitted! Awaiting approval.')
                return redirect('transactions')
        else:
            form = WithdrawalForm()
        
        context = {'form': form, 'profile': profile, 'step': 'withdraw'}
        return render(request, 'core/withdrawal.html', context)


@login_required
def transactions_view(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    task_history = TaskCompletion.objects.filter(user=request.user).order_by('-completed_at')
    
    context = {
        'transactions': transactions,
        'task_history': task_history,
    }
    return render(request, 'core/transactions.html', context)


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    context = {
        'profile': profile,
    }
    return render(request, 'core/profile.html', context)


@login_required
def profile_edit_view(request):
    from .forms import ProfileEditForm
    
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            profile = form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'core/profile_edit.html', context)
