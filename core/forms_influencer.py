from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import InfluencerProfile, Task


class InfluencerSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
        'placeholder': 'Email Address'
    }))
    
    company_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
        'placeholder': 'Company Name (Optional)'
    }))
    
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
        'placeholder': 'Phone Number'
    }))
    
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
        'placeholder': 'Website URL (Optional)'
    }))
    
    social_media = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
        'placeholder': 'Social Media Links (Optional)'
    }))
    
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
        'placeholder': 'Tell us about yourself and your business',
        'rows': 4
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
            'placeholder': 'Confirm Password'
        })


class InfluencerTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'task_type', 'category', 'video_url', 'channel_url', 'points', 'duration_seconds', 'max_completions', 'expires_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
                'placeholder': 'Task Title'
            }),
            'task_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
                'placeholder': 'https://youtube.com/watch?v=...'
            }),
            'channel_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
                'placeholder': 'https://youtube.com/@channelname (optional)'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
                'placeholder': '100 or 150'
            }),
            'duration_seconds': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
                'placeholder': '50'
            }),
            'max_completions': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
                'placeholder': '100'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-primary text-white',
                'type': 'datetime-local'
            }),
        }
