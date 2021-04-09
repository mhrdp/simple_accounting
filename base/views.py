from django.shortcuts import render

# Create your views here.

def index(request):
    content = {

    }
    return render(request, 'base/base_test.html', content)