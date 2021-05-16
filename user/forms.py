from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm
    )
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django import forms

from .models import (
    CompanyDetail, UserExtended, Industry, UserPreferences
)

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Email/Username',
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder': 'Username/Email',
                }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class':'form-control',
                'placeholder': 'Password',
                }
        )
    )

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )

class ResetPasswordForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com',
                },
        )
    )
    def clean_email(self):
        UserModel = get_user_model()
        email = self.cleaned_data['email']
        if not UserModel.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError(_('Sorry, no such email in our database'), code='invalid')
        return email

class CompanyDetailForm(forms.ModelForm):
    company_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class':'form-control'}
        ),
        required=True
    )
    company_description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class':'form-control',
                'placeholder':'Describe shortly about your company',
                }
        ),
        required=False,
    )
    industry = forms.ModelChoiceField(
        queryset=Industry.objects.all().order_by('-pk'),
        widget=forms.Select(
            attrs={'class':'form-control'}
        ),
        required=True,
    )
    class Meta:
        model = CompanyDetail
        fields = [
            'company_name', 'company_description', 'industry'
        ]

class UserForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class':'form-control'}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class':'form-control'}
        )
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class':'form-control'}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class':'form-control'}
        )
    )
    class Meta:
        model = UserExtended
        fields = [
            'username', 'email', 'first_name', 'last_name'
        ]

class UserPreferencesDB(forms.ModelForm):
    DARK = 'Dark'
    LIGHT = 'Light'
    UI_MODE = [
        (DARK, 'Dark'),
        (LIGHT, 'Light'),
    ]

    light_dark_mode = forms.ChoiceField(
        choices=UI_MODE,
        widget=forms.Select(
            attrs={'class':'form-control form-control-sm'}
        )
    )
    class Meta:
        model = UserPreferences
        fields = [
            'light_dark_mode'
        ]

#class CompanyIndustryForm(forms.ModelForm):
#    FNB = 'Food and Beverages'
#    DSG = 'Design'
#    IT = 'Technology'
#    OTR = 'Others'
#    INDUSTRIES = [
#        (FNB, 'Food and Beverages'),
#        (DSG, 'Design'),
#        (IT, 'Technology'),
#        (OTR, 'Others'),
#    ]
#    
#    industry = forms.ChoiceField(
#        choices=INDUSTRIES,
#        widget=forms.Select(
#            attrs={'class':'form-control'},
#        )
#    )
#    class Meta:
#        model = CompanyIndustry
#        fields = [
#            'industry'
#        ]