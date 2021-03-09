from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import views as auth_views
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.urls import reverse_lazy

from .forms import LoginForm, CompanyDetailForm, CompanyIndustryForm
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
    content = {
        'profile': profile
    }
    return render(request, 'user/profile.html', content)

def company_profile_edit(request):
    form_description = CompanyDetailForm()
    form_industry = CompanyIndustryForm()
    if form_description and form_industry:
        form_description = CompanyDetailForm()
        form_industry = CompanyIndustryForm()
    else:
        description = get_object_or_404(CompanyDetail, username=request.user.pk)
        industry = get_object_or_404(CompanyIndustry, username=request.user.pk)
        if not description and not industry:
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
    logout(request)
    content = {
        
    }
    return render(request, 'user/logout.html', content)