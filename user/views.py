from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.contrib.auth import views as auth_views
from django.contrib.auth import (
    logout, get_user_model, update_session_auth_hash
    )
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.urls import reverse_lazy

from .forms import (
    LoginForm, CompanyDetailForm, CompanyIndustryForm,
    ChangePasswordForm
    )
from .models import CompanyDetail, CompanyIndustry

# Create your views here.
# Class Based
class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'user/login.html'



# Function Based
@login_required
def company_profile(request):
    UserModel = get_user_model()
    profile = get_object_or_404(UserModel, username=request.user.username)

    description_empty = CompanyDetail.objects.filter(username=request.user.pk)
    industry_empty = CompanyIndustry.objects.filter(username=request.user.pk)
    if not description_empty and not industry_empty:
        return redirect('edit')
    else:
        company_description = get_object_or_404(CompanyDetail, username=request.user.pk)
        company_industry = get_object_or_404(CompanyIndustry, username=request.user.pk)

    content = {
        'profile': profile,
        'company_description': company_description,
        'company_industry': company_industry,
    }
    return render(request, 'user/profile.html', content)

@login_required
def company_profile_edit(request):
    description_empty = CompanyDetail.objects.filter(username=request.user.pk)
    industry_empty = CompanyIndustry.objects.filter(username=request.user.pk)
    if not description_empty and not industry_empty:
        form_description = CompanyDetailForm()
        form_industry = CompanyIndustryForm()
        if request.method == 'POST':
            form_description = CompanyDetailForm(request.POST or None)
            form_industry = CompanyIndustryForm(request.POST or None)
            if form_description.is_valid() and form_industry.is_valid():
                save_form_description = form_description.save(commit=False)
                save_form_industry = form_industry.save(commit=False)

                save_form_description.username = request.user
                save_form_industry.username = request.user
                save_form_industry.save()
                save_form_description.save()

                return redirect('profile')
    else:
        description = get_object_or_404(CompanyDetail, username=request.user.pk)
        industry = get_object_or_404(CompanyIndustry, username=request.user.pk)
        form_description = CompanyDetailForm(
            request.POST or None, instance=description
            )
        form_industry = CompanyIndustryForm(
            request.POST or None, instance=industry
        )
        if form_description.is_valid() and form_industry.is_valid():
            form_description.save()
            form_industry.save()

            return redirect('profile')
    
    content = {
        'form_description': form_description,
        'form_industry': form_industry,
    }
    return render(request, 'user/update.html', content)

@login_required
def user_logout(request):
    if logout(request):
        return redirect('logout')
    content = {
        
    }
    return render(request, 'user/logout.html', content)

@login_required
def user_change_password(request):
    password_change_notification = ''
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            password_form = form.save()
            update_session_auth_hash(request, password_form)

            password_change_notification = "Success!"
            return redirect('profile')
        else:
            password_change_notification = "Something went wrong!"
    else:
        form = ChangePasswordForm(request.user)
    content = {
        'password_change_notification': password_change_notification,
        'form': form,
    }
    return render(request, 'user/change_password.html', content)