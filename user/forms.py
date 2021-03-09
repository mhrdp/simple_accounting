from django.contrib.auth.forms import AuthenticationForm

from django import forms

from .models import CompanyDetail, CompanyIndustry

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Email/Username',
        widget=forms.TextInput(
            attrs={'class':'form-control'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class':'form-control'}
        )
    )

class CompanyDetailForm(forms.ModelForm):
    company_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class':'form-control'}
        )
    )
    company_description = forms.CharField(
        widget=forms.Textarea(
            attrs={'class':'form-control'}
        )
    )
    class Meta:
        model = CompanyDetail
        fields = [
            'company_name', 'company_description'
        ]

class CompanyIndustryForm(forms.ModelForm):
    FNB = 'Food and Beverages'
    DSG = 'Design'
    IT = 'Technology'
    OTR = 'Others'
    INDUSTRIES = [
        (FNB, 'Food and Beverages'),
        (DSG, 'Design'),
        (IT, 'Technology'),
        (OTR, 'Others'),
    ]
    
    industry = forms.ChoiceField(
        choices=INDUSTRIES,
        widget=forms.Select(
            attrs={'class':'form-control'},
        )
    )
    class Meta:
        model = CompanyIndustry
        fields = [
            'industry'
        ]