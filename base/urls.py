from django.urls import path

from . import views as index_views

urlpatterns = [
    path('a/', index_views.index, name='index'),
]