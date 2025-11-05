from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import random

from .models import InfluencerProfile, EmailVerification
from .forms_influencer import InfluencerSignUpForm


@login_required
def upgrade_to_influencer_view(request):
    if hasattr(request.user, 'influencer_profile'):
        messages.info(request, 'You are already an influencer!')
        return redirect('influencer_dashboard')
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '')
        company_name = request.POST.get('company_name', '')
        website = request.POST.get('website', '')
        social_media = request.POST.get('social_media', '')
        bio = request.POST.get('bio', '')
        
        InfluencerProfile.objects.create(
            user=request.user,
            phone_number=phone_number,
            company_name=company_name,
            website=website,
            social_media=social_media,
            bio=bio,
            is_verified=False,
            status='pending'
        )
        
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
                'Ken - Influencer Email Verification',
                get_otp_email_text(request.user.username, otp_code),
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
                html_message=get_otp_email_html(request.user.username, otp_code)
            )
            messages.success(request, f'Verification code sent to {request.user.email}')
        except:
            messages.warning(request, f'Email not sent. Your OTP code is: {otp_code}')
        
        return redirect('influencer_verify_email')
    
    return render(request, 'core/upgrade_to_influencer.html')
