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
    LoginForm, CompanyDetailForm,
    ChangePasswordForm, UserForm
    )
from .models import CompanyDetail

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
    profile = get_object_or_404(UserModel, username=request.user.username)

    description_empty = CompanyDetail.objects.filter(username=request.user.pk)

    if not description_empty:
        return redirect('edit')
    else:
        company_description = get_object_or_404(CompanyDetail, username=request.user.pk)

    content = {
        'profile': profile,
        'company_description': company_description,
    }
    return render(request, 'user/profile.html', content)

@login_required
def company_profile_edit(request):
    first_time_msg = ''
    description_empty = CompanyDetail.objects.filter(username=request.user.pk)

    # if fields empty
    if not description_empty:
        first_time_msg = 'For your convenience, please fill this form'
        form_description = CompanyDetailForm()
        if request.method == 'POST':
            form_description = CompanyDetailForm(request.POST or None)
            if form_description.is_valid():
                save_form_description = form_description.save(commit=False)

                save_form_description.username = request.user

                save_form_description.save()
                return redirect('profile')
    else:
        description = get_object_or_404(CompanyDetail, username=request.user.pk)

        if request.method == 'POST':
            form_description = CompanyDetailForm(
                request.POST or None, instance=description
                )
            if form_description.is_valid():
                form_description.save()

                return redirect('profile')
        else:
            form_description = CompanyDetailForm(
                request.POST or None, instance=description
                )
    
    content = {
        'form_description': form_description,
        'first_time_msg': first_time_msg,
    }
    return render(request, 'user/update.html', content)

@login_required
def user_profile_edit(request):
    update_error = ''
    if request.method == 'POST':
        user_form = UserForm(request.POST or None, instance=request.user)
        if user_form.is_valid():
            user_form.save()

            return redirect('profile')
        else:
            update_error = 'There\'s an error in data'
    else:
        user_form = UserForm(instance=request.user)
    
    content = {
        'user_form': user_form,
        'update_error': update_error,
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