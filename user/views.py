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
    logging_out = logout(request)
    if logging_out:
        return redirect('logout')
    content = {
        
    }
    return render(request, 'user/logout.html', content)