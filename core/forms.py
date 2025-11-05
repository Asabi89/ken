from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Task, Transaction, UserProfile, TaskCompletion


class SignUpForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('user', 'Regular User - Complete tasks and earn money'),
        ('influencer', 'Influencer/Business - Create tasks and promote'),
    )
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'user-type-radio'
        }),
        initial='user'
    )
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
        'placeholder': 'Email'
    }))
    phone_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
        'placeholder': 'Phone Number (Optional)'
    }))
    
    company_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
        'placeholder': 'Company Name (for influencers)'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
            'placeholder': 'Confirm Password'
        })


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
        'placeholder': 'Password'
    }))


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'task_type', 'video_url', 'channel_url', 'points', 'usd_value', 'duration_seconds', 'max_completions']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'placeholder': 'Task Title'
            }),
            'task_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'placeholder': 'https://youtube.com/watch?v=...'
            }),
            'channel_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'placeholder': 'https://youtube.com/@channelname (optional)'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'placeholder': '100'
            }),
            'usd_value': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'placeholder': '0.50'
            }),
            'duration_seconds': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'placeholder': '50'
            }),
            'max_completions': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'placeholder': '100'
            }),
        }


class WithdrawalSetupForm(forms.ModelForm):
    pin = forms.CharField(max_length=6, min_length=6, widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white text-center text-2xl tracking-widest',
        'placeholder': '••••••',
        'maxlength': '6'
    }))
    confirm_pin = forms.CharField(max_length=6, min_length=6, widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white text-center text-2xl tracking-widest',
        'placeholder': '••••••',
        'maxlength': '6'
    }))
    
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'mobile_money_provider']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'placeholder': 'Phone Number',
                'required': 'required'
            }),
            'mobile_money_provider': forms.Select(choices=[
                ('', 'Select Provider'),
                ('Wave', 'Wave'),
                ('MTN', 'MTN Mobile Money'),
                ('Moov', 'Moov Money'),
                ('Orange', 'Orange Money'),
            ], attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'required': 'required'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        pin = cleaned_data.get('pin')
        confirm_pin = cleaned_data.get('confirm_pin')
        
        if pin and confirm_pin and pin != confirm_pin:
            raise forms.ValidationError('PINs do not match')
        
        return cleaned_data


class VerifyOTPForm(forms.Form):
    otp_code = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white text-center text-3xl tracking-widest',
        'placeholder': '• • • • • •',
        'maxlength': '6',
        'autocomplete': 'off'
    }))


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount_usd', 'phone_number', 'mobile_money_provider']
        widgets = {
            'amount_usd': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'placeholder': 'Amount ($)',
                'min': '50'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'placeholder': 'Phone Number'
            }),
            'mobile_money_provider': forms.Select(choices=[
                ('', 'Select Provider'),
                ('Wave', 'Wave'),
                ('MTN', 'MTN Mobile Money'),
                ('Moov', 'Moov Money'),
                ('Orange', 'Orange Money'),
            ], attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white'
            }),
        }


class TaskCompletionForm(forms.ModelForm):
    class Meta:
        model = TaskCompletion
        fields = ['proof_screenshot']
        widgets = {
            'proof_screenshot': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'proof_screenshot_input',
                'accept': 'image/*',
                'required': 'required'
            }),
        }


class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
        'placeholder': 'Email'
    }))
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone_number', 'mobile_money_provider']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'profile_picture_input',
                'accept': 'image/*'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white',
                'placeholder': 'Phone Number'
            }),
            'mobile_money_provider': forms.Select(choices=[
                ('', 'Select Provider'),
                ('Wave', 'Wave'),
                ('MTN', 'MTN Mobile Money'),
                ('Moov', 'Moov Money'),
                ('Orange', 'Orange Money'),
            ], attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-green-500 text-white'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
