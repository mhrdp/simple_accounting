from django.shortcuts import render, redirect
from user.models import UserPreferences
from django.shortcuts import get_object_or_404
# Create your views here.

def base(request):
    ui_config = UserPreferences.objects.filter(
        username=request.user.pk
    ).values(
        'light_dark_mode'
    )

    config = get_object_or_404(UserPreferences, username=request.user)
    content = {
        'ui_config': ui_config,
        'config': config,
    }
    #return render(request, 'base/base_test.html', content)
    return redirect('login')