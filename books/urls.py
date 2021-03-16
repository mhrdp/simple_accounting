from django.urls import path

from . import views as books_views

urlpatterns = [
    path('product/new/', books_views.register_product, name='register_product'),
    path('books/income/new/', books_views.register_income, name='register_income'),
    path('books/expense/new/', books_views.register_expense, name='register_expense'),

    path('books/ajax', books_views.expense_dropdown_ajax, name='dropdown_ajax'),
]
