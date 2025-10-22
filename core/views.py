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
        return redirect('dashboard')
    return render(request, 'core/landing.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone_number = form.cleaned_data.get('phone_number')
            UserProfile.objects.create(user=user, phone_number=phone_number)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
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
            cfa_earned=task.cfa_value,
            is_verified=False if needs_proof else True,
            proof_screenshot=request.FILES.get('proof_screenshot') if needs_proof else None
        )
        
        if not needs_proof:
            profile.total_points += task.points
            profile.total_earned_cfa += task.cfa_value
            profile.available_balance_cfa += task.cfa_value
            profile.save()
            
            Transaction.objects.create(
                user=request.user,
                transaction_type='earning',
                amount_cfa=task.cfa_value,
                points=task.points,
                status='completed'
            )
        
        task.current_completions += 1
        task.save()
        
        if needs_proof:
            messages.success(request, 'Task submitted! Waiting for admin verification.')
        else:
            messages.success(request, f'Task completed! You earned {task.points} points and {task.cfa_value} CFA!')
        
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
                
                email_html = f"""
                <html>
                <body style="margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; background-color: #000000;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #121212;">
                        <div style="background: linear-gradient(135deg, #32CD32 0%, #28a428 100%); padding: 40px 20px; text-align: center;">
                            <h1 style="color: #000000; font-size: 36px; margin: 0; font-weight: bold;">Ken</h1>
                            <p style="color: #000000; margin: 10px 0 0 0; font-size: 14px;">Earn Money Online</p>
                        </div>
                        
                        <div style="padding: 40px 30px; background-color: #1a1a1a; border-left: 4px solid #32CD32;">
                            <h2 style="color: #ffffff; font-size: 24px; margin: 0 0 20px 0;">Email Verification</h2>
                            <p style="color: #cccccc; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                Hello <strong style="color: #32CD32;">{request.user.username}</strong>,
                            </p>
                            <p style="color: #cccccc; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                Use the code below to verify your email and complete your withdrawal setup:
                            </p>
                            
                            <div style="background-color: #000000; border: 2px dashed #32CD32; border-radius: 12px; padding: 30px; text-align: center; margin: 30px 0;">
                                <div style="color: #32CD32; font-size: 48px; font-weight: bold; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                    {otp_code}
                                </div>
                            </div>
                            
                            <p style="color: #999999; font-size: 14px; line-height: 1.6; margin: 20px 0 0 0;">
                                ⏱️ This code expires in <strong style="color: #32CD32;">10 minutes</strong>
                            </p>
                            <p style="color: #999999; font-size: 14px; line-height: 1.6; margin: 10px 0 0 0;">
                                🔒 If you didn't request this code, please ignore this email.
                            </p>
                        </div>
                        
                        <div style="background-color: #0a0a0a; padding: 30px; text-align: center; border-top: 1px solid #2a2a2a;">
                            <p style="color: #666666; font-size: 12px; margin: 0 0 10px 0;">
                                © 2025 Ken. All rights reserved.
                            </p>
                            <p style="color: #666666; font-size: 12px; margin: 0;">
                                Complete tasks, earn money instantly
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                try:
                    send_mail(
                        'Ken - Email Verification Code',
                        f'Your verification code is: {otp_code}\n\nThis code expires in 10 minutes.',
                        settings.DEFAULT_FROM_EMAIL,
                        [request.user.email],
                        fail_silently=False,
                        html_message=email_html
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
                amount = form.cleaned_data['amount_cfa']
                
                if amount < 5000:
                    messages.error(request, 'Minimum withdrawal is 5000 CFA!')
                    return redirect('/withdrawal/?step=withdraw')
                
                if amount > profile.available_balance_cfa:
                    messages.error(request, 'Insufficient balance!')
                    return redirect('/withdrawal/?step=withdraw')
                
                withdrawal = form.save(commit=False)
                withdrawal.user = request.user
                withdrawal.transaction_type = 'withdrawal'
                withdrawal.status = 'pending'
                withdrawal.save()
                
                profile.available_balance_cfa -= amount
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
