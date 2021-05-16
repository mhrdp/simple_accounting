from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings

from django.contrib.auth import get_user, views as auth_views
from django.contrib.auth import (
    logout, get_user_model, update_session_auth_hash
    )
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.views import generic
from django.urls import reverse_lazy

from .forms import (
    LoginForm, CompanyDetailForm,
    ChangePasswordForm, UserForm, UserPreferencesDB
    )
from .models import CompanyDetail, UserPreferences

import json

# Create your views here.
# Class Based
class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'user/login.html'



# Function Based
def index(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return redirect('profile')
    content = {}
    return render(request, 'base/index.html', content)
    
@login_required
def company_profile(request):
    UserModel = get_user_model()
    profile = get_object_or_404(UserModel, username=request.user)

    description_empty = CompanyDetail.objects.filter(username=request.user.pk)
    test = UserPreferences.objects.filter(
        username=request.user.pk
    ).values(
        'light_dark_mode'
    )

    if not description_empty:
        return redirect('edit')
    else:
        company_description = get_object_or_404(CompanyDetail, username=request.user.pk)

    content = {
        'profile': profile,
        'company_description': company_description,
        'test': test[0]['light_dark_mode'],
    }
    return render(request, 'user/profile.html', content)

@login_required
def company_profile_edit(request):
    description_empty = CompanyDetail.objects.filter(username=request.user.pk)

    # if fields empty
    if not description_empty:
        messages.info(request, 'Lengkapi profil singkat perusahaan Anda')
        form_description = CompanyDetailForm()
        if request.method == 'POST':
            form_description = CompanyDetailForm(request.POST or None)
            if form_description.is_valid():
                save_form_description = form_description.save(commit=False)

                save_form_description.username = request.user

                save_form_description.save()
                messages.success(request, 'Profil perusahaan sudah di update')
                return redirect('profile')
    else:
        description = get_object_or_404(CompanyDetail, username=request.user.pk)

        if request.method == 'POST':
            form_description = CompanyDetailForm(
                request.POST or None, instance=description
                )
            if form_description.is_valid():
                form_description.save()
                messages.success(request, 'Profil perusahaan sudah di update')
                return redirect('profile')
        else:
            form_description = CompanyDetailForm(
                request.POST or None, instance=description
                )
    
    content = {
        'form_description': form_description,
    }
    return render(request, 'user/update.html', content)

@login_required
def user_profile_edit(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST or None, instance=request.user)
        if user_form.is_valid():
            user_form.save()

            messages.success(request, 'Update berhasil!')
            return redirect('profile')
        else:
            messages.error(request, 'Ada kesalahan dalam proses update, harap coba kembali.')
    else:
        user_form = UserForm(instance=request.user)
    
    content = {
        'user_form': user_form,
    }
    return render(request, 'user/user_update.html', content)

@login_required
def user_logout(request):
    if logout(request):
        return redirect('logout')
    content = {
        
    }
    return render(request, 'user/logout.html', content)

@login_required
def user_change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            password_form = form.save()
            update_session_auth_hash(request, password_form)

            messages.success(request, 'Anda Berhasil mengganti password')
            return redirect('profile')
        else:
            messages.error(request, 'Ada kesalahan pada proses, harap coba kembali')
    else:
        form = ChangePasswordForm(request.user)
    content = {
        'form': form,
    }
    return render(request, 'user/change_password.html', content)

# This might be unecessary for now, but I'll keep it just in case
@login_required
def user_setting(request):
    settings_obj = UserPreferences.objects.filter(
        username=request.user.pk
    )
    if not settings_obj:
        settings_form = UserPreferencesDB()
        if request.method == 'POST':
            settings_form = UserPreferencesDB(request.POST or None)
            if settings_form.is_valid():
                save = settings_form.save(commit=False)
                save.username = request.user

                messages.success(request, 'Setting berhasil di update')
                save.save()
            else:
                messages.error(request, 'Ada kesalahan dalam pengaturan')
    else:
        settings_data = get_object_or_404(UserPreferences, username=request.user)
        if request.method == 'POST':
            settings_form = UserPreferencesDB(request.POST or None, instance=settings_data)
            if settings_form.is_valid():
                save = settings_form.save(commit=False)
                save.username = request.user
                save.save()
                
                messages.success(request, 'Setting berhasil di update')
            else:
                messages.error(request, 'Ada kesalahan dalam pengaturan')
                settings_form = UserPreferencesDB(instance=settings_data)
        else:
            settings_form = UserPreferencesDB(instance=settings_data)
    content = {
        'user_preferences_form': settings_form,
    }
    return render(request, 'user/settings.html', content)

# def user_setting_ajax(request):
#    user_preferences = request.POST.get('user_preferences')
#    user_preferences_db = UserPreferencesDB(request.POST or None)
#    user_preferences_data = None
#
#    if request.is_ajax():
#        user_preferences_data = json.loads(user_preferences)
#        save_preferences = user_preferences_db.save(commit=False)
#
#        save_preferences.light_dark_mode = user_preferences_data['darkLightPreference']
#        save_preferences.username = request.user
#        save_preferences.save()
#
#    content = {
#        'user_preferences_data': user_preferences_data,
#    }
#    return render(request, 'user/user_setting.html', content)